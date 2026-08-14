from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


def git_blob(root: Path, commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{path}"],
        check=True,
        capture_output=True,
    ).stdout


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def metric(
    name: str,
    values: list[float],
    unit: str,
    direction: str,
    failures: int,
) -> dict[str, Any]:
    return {
        "name": name,
        "value": statistics.median(values),
        "unit": unit,
        "direction": direction,
        "samples": values,
        "failures": failures,
        "summary": {
            "min": min(values),
            "max": max(values),
            "mean": statistics.fmean(values),
            "median": statistics.median(values),
        },
    }


def effective_workload(
    template: dict[str, Any], rows: int, repetitions: int
) -> dict[str, Any]:
    effective = dict(template)
    effective["measured_rows_per_repetition"] = rows
    effective["repetitions"] = repetitions
    return effective


def build(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    workload_template = json.loads(
        git_blob(root, args.source_commit, args.workload_ref)
    )
    workload = effective_workload(workload_template, args.rows, args.repetitions)
    runs = summary["runs"]
    if len(runs) != args.repetitions:
        raise ValueError("raw run count differs from workload repetitions")
    if any(int(run["environment"]["rows"]) != args.rows for run in runs):
        raise ValueError("raw run row count differs from executed rows")
    failures = sum(int(run["failures"]) for run in runs)
    if failures:
        raise ValueError(f"benchmark runs contain {failures} failure(s)")

    def samples(field: str) -> list[float]:
        return [float(run["metrics"][field]) for run in runs]

    metrics = [
        metric("invalid_row_detection_f1", samples("f1"), "ratio", "higher_is_better", failures),
        metric("rejected_rows_percent", samples("rejected_rows_percent"), "percent", "target", failures),
        metric("reason_exact_match_rate", samples("reason_exact_match_rate"), "ratio", "higher_is_better", failures),
        metric("throughput_rows_per_second", samples("throughput_rows_per_second"), "rows_per_second", "higher_is_better", failures),
        metric("duration_ms", [value * 1000 for value in samples("duration_seconds")], "milliseconds", "lower_is_better", failures),
        metric("false_positive_count", samples("false_positive"), "count", "target", failures),
        metric("false_negative_count", samples("false_negative"), "count", "target", failures),
    ]
    first = runs[0]
    fixture_digest = "sha256:" + first["proof"]["fixture_sha256"]
    if any("sha256:" + run["proof"]["fixture_sha256"] != fixture_digest for run in runs):
        raise ValueError("fixture digest differs between repetitions")

    result = {
        "schema_version": 2,
        "run_id": str(uuid.uuid4()),
        "project": "data-quality-checks",
        "benchmark_id": workload["benchmark_id"],
        "workload": {
            "version": "labeled-order-quality-gate-v1",
            "fixture_digest": fixture_digest,
            "config_digest": digest(
                json.dumps(workload, sort_keys=True, separators=(",", ":")).encode()
            ),
            "warmup_iterations": workload["warmup_rows"],
            "measured_iterations": args.rows,
            "concurrency": workload["concurrency"],
        },
        "metrics": metrics,
        "execution": {
            "command": args.command,
            "started_at": min(run["timestamp"] for run in runs),
            "duration_seconds": sum(samples("duration_seconds")),
            "exit_code": 0,
            "repeat": len(runs),
        },
        "environment": {
            "runtime": f"python-{first['environment']['python']}",
            "architecture": first["environment"]["machine"],
            "hardware_class": args.hardware_class,
            "container_platform": first["environment"]["platform"],
            "pandera": first["environment"]["pandera"],
            "polars": first["environment"]["polars"],
        },
        "provenance": {
            "source_commit": args.source_commit,
            "clean_tree": True,
            "image_ref": args.image_ref,
            "image_digest": args.image_digest,
            "dependency_lock_digest": digest(
                git_blob(root, args.source_commit, args.lock_ref)
            ),
            "producer": args.producer,
            "artifact_digest": args.artifact_digest,
        },
        "comparability_key": (
            "data-quality-checks:labeled-orders-v1:"
            f"rows-{args.rows}:seed-42:"
            "pandera-0_32_1:polars-1_42_1"
        ),
    }
    schema = json.loads(
        (root / ".portfolio/contracts/benchmark-result-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--image-ref", required=True)
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--artifact-digest", required=True)
    parser.add_argument("--hardware-class", required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--repetitions", type=int, required=True)
    parser.add_argument("--producer", choices=("local", "github-actions", "other-ci"), required=True)
    parser.add_argument("--workload-ref", default="benchmarks/workload.json")
    parser.add_argument("--lock-ref", default="constraints.lock")
    parser.add_argument("--command", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build(args), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
