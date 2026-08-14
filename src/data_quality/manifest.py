from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from data_quality.domain import QualityOutcome


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_validated_batch_manifest(
    *,
    manifest_path: Path,
    dataset_id: str,
    dataset_version: str,
    contract_path: Path,
    input_path: Path,
    accepted_path: Path,
    quarantine_path: Path,
    outcome: QualityOutcome,
) -> dict[str, Any]:
    paths = {
        path.resolve()
        for path in (input_path, accepted_path, quarantine_path, contract_path)
    }
    if manifest_path.resolve() in paths:
        raise ValueError("manifest path must not overwrite an input, output, or contract")

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    rejected_rows = len(outcome.rejections)
    manifest = {
        "schema_version": 1,
        "dataset": {"id": dataset_id, "version": dataset_version},
        "contract": {
            "id": contract["contract_id"],
            "sha256": _digest(contract_path),
        },
        "source": {
            "uri": str(input_path),
            "format": "csv",
            "sha256": _digest(input_path),
            "rows": outcome.total_rows,
        },
        "artifacts": {
            "accepted": {
                "uri": str(accepted_path),
                "format": "csv",
                "sha256": _digest(accepted_path),
                "rows": outcome.accepted_rows,
            },
            "quarantine": {
                "uri": str(quarantine_path),
                "format": "csv",
                "sha256": _digest(quarantine_path),
                "rows": rejected_rows,
            },
        },
        "quality": {
            "status": "passed",
            "total_rows": outcome.total_rows,
            "accepted_rows": outcome.accepted_rows,
            "rejected_rows": rejected_rows,
            "rejected_rows_percent": (
                100.0 * rejected_rows / outcome.total_rows if outcome.total_rows else 0.0
            ),
            "reason_counts": dict(outcome.reason_counts),
        },
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest
