from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from data_quality.application import execute_gate
from data_quality.benchmark import run_benchmark
from data_quality.polars_engine import PolarsPanderaQualityEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="data-quality-checks")
    subparsers = parser.add_subparsers(dest="command", required=True)

    benchmark = subparsers.add_parser("benchmark")
    benchmark.add_argument("--rows", type=int, default=100_000)
    benchmark.add_argument(
        "--output",
        type=Path,
        default=Path(
            os.getenv(
                "BENCHMARK_OUTPUT",
                "benchmarks/results/summary.json",
            )
        ),
    )

    gate = subparsers.add_parser("gate")
    gate.add_argument("input", type=Path)
    gate.add_argument("--accepted", type=Path, required=True)
    gate.add_argument("--quarantine", type=Path, required=True)
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    arguments = list(argv if argv is not None else sys.argv[1:])
    if not arguments:
        arguments = ["benchmark"]
    args = build_parser().parse_args(arguments)
    if args.command == "benchmark":
        result = run_benchmark(args.output, rows=args.rows)
    else:
        outcome = execute_gate(
            PolarsPanderaQualityEngine(),
            args.input,
            args.accepted,
            args.quarantine,
        )
        result = {
            "total_rows": outcome.total_rows,
            "accepted_rows": outcome.accepted_rows,
            "rejected_rows": len(outcome.rejections),
            "reason_counts": dict(outcome.reason_counts),
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def main() -> int:
    argv = sys.argv[1:] or ["benchmark"]
    try:
        return run(argv)
    except Exception as error:
        failure = {
            "project": "data-quality-checks",
            "timestamp": datetime.now(UTC)
            .isoformat()
            .replace("+00:00", "Z"),
            "error_type": type(error).__name__,
            "error": str(error),
        }
        path = Path("benchmarks/results/failure.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps(failure, sort_keys=True), file=sys.stderr)
        return 1
