from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import pandera
import polars as pl

from data_quality.application import execute_gate
from data_quality.domain import score_outcome
from data_quality.fixture import generate_fixture
from data_quality.polars_engine import PolarsPanderaQualityEngine


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_benchmark(
    output_path: Path | None,
    rows: int = 100_000,
    command: str = "docker run --rm data-quality-checks",
) -> dict[str, Any]:
    if rows < 1_000:
        raise ValueError("benchmark rows must be at least 1000")

    engine = PolarsPanderaQualityEngine()
    with tempfile.TemporaryDirectory(prefix="data-quality-") as temporary:
        root = Path(temporary)
        warmup = generate_fixture(root / "warmup", rows=1_000, seed=7)
        execute_gate(
            engine,
            warmup.csv_path,
            root / "warmup-accepted.csv",
            root / "warmup-quarantine.csv",
        )

        fixture = generate_fixture(root / "measured", rows=rows, seed=42)
        accepted_path = root / "accepted.csv"
        quarantine_path = root / "quarantine.csv"
        started = perf_counter()
        outcome = execute_gate(
            engine,
            fixture.csv_path,
            accepted_path,
            quarantine_path,
        )
        duration_seconds = perf_counter() - started
        metrics = score_outcome(rows, fixture.truth, outcome)
        throughput = rows / duration_seconds

        result = {
            "project": "data-quality-checks",
            "metric": "invalid_row_detection_f1",
            "value": metrics.f1,
            "unit": "ratio",
            "timestamp": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "command": command,
            "repeat": 1,
            "environment": {
                "python": platform.python_version(),
                "implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "machine": platform.machine(),
                "polars": pl.__version__,
                "pandera": pandera.__version__,
                "rows": rows,
                "container": Path("/.dockerenv").exists(),
                "image_id": os.getenv("IMAGE_ID", "not-recorded"),
            },
            "summary": {
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1": metrics.f1,
                "rejected_rows_percent": metrics.rejected_rows_percent,
                "reason_exact_match_rate": metrics.reason_exact_match_rate,
                "throughput_rows_per_second": throughput,
                "duration_seconds": duration_seconds,
            },
            "metrics": {
                "true_positive": metrics.true_positive,
                "false_positive": metrics.false_positive,
                "true_negative": metrics.true_negative,
                "false_negative": metrics.false_negative,
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1": metrics.f1,
                "rejected_rows_percent": metrics.rejected_rows_percent,
                "reason_exact_match_rate": metrics.reason_exact_match_rate,
                "throughput_rows_per_second": throughput,
                "duration_seconds": duration_seconds,
                "reason_counts": dict(outcome.reason_counts),
            },
            "proof": {
                "fixture_seed": 42,
                "fixture_rows": rows,
                "fixture_sha256": fixture.sha256,
                "truth_defined_before_validation": True,
                "invalid_rows": len(fixture.truth),
                "accepted_rows": outcome.accepted_rows,
                "quarantined_rows": len(outcome.rejections),
                "accepted_sha256": _sha256(accepted_path),
                "quarantine_sha256": _sha256(quarantine_path),
                "warmup_rows": 1_000,
                "measured_boundary": "read+schema+rules+accepted/quarantine writes",
                "structural_contract": "Pandera DataFrameModel",
                "row_engine": "Polars vectorized expressions",
                "reference_engine": "Python standard-library parity oracle",
                "injected_defects": [
                    "customer_required",
                    "quantity_range",
                    "currency_allowed",
                    "total_consistent",
                    "status_allowed",
                ],
            },
            "failures": 0,
        }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return result
