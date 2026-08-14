# Intent: data-quality-checks

## Measurable Claim

One local-first Docker command applies a strict structural contract, quarantines rule violations with exact reason IDs, proves Polars/Pandera parity against a Python oracle, and scores invalid-row detection F1, rejected percentage, and full-gate throughput.

## Problem

Protects the input side of #21 by failing corrupted batches closed and partitioning readable rows into accepted and reason-coded quarantine artifacts before training or analytics.

## In Scope

- Use the selected component pack: `mlops-data-platform`.
- Keep the project under the MLOps and Data Platform program.
- Preserve the benchmark contract: `invalid_row_detection_f1` in `benchmarks/results/summary.json`.
- Keep the default path local-first and reproducible.

## Out Of Scope

- Paid credentials for the default demo.
- External infrastructure that is not required by the benchmark.
- Replacing local portfolio skills with external components silently.

## Default Demo Path

- Status: implemented
- Runtime: Single non-root Python 3.12.13 container pinned by OCI digest; eager local DataFrame validation and deterministic CPU benchmark.
- Benchmark command: `docker run --rm data-quality-checks`

## Public Proof

- Benchmark: invalid_row_detection_f1 = 1.0000; median throughput = 617,445.89 rows/s
- Result path: `benchmarks/results/summary.json`
