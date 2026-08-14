# Agent Handoff: data-quality-checks

## Objective

Finish #26 as the strict input-quality gate in the MLOps and Data Platform system before #21 trains or analytics consume a batch.

## Accepted

- Pipeline architecture with a real `QualityEngine` substitution boundary.
- Pandera eager structural contract.
- Polars vectorized measured engine.
- Standard-library/Decimal oracle.
- Batch-fatal structural errors; row-level quarantine with ordered reasons.
- F1 primary; rejected percentage, exact reason, and throughput secondary.
- No DuckDB, Great Expectations, Spark, API, broker, DB, cloud, Airflow, or MLflow.

## Current State

- Domain, fixture, oracle, optimized adapter, manifest contract, benchmark producer, CLI, tests, Docker, README, SDD, and references are implemented.
- Baseline Docker verification passed 23 tests at 94.65% coverage before the manifest/V2 additions.
- Publication requires a clean source commit, three canonical runs, final documentation alignment, push to `main`, and exact-head CI.

## Docker Order

1. Run Ruff and all tests in the rebuilt locked-wheel image.
2. Commit the clean benchmark source.
3. Run `./tools/benchmark.ps1` for three 100,000-row repetitions.
4. Inspect V2 workload/repetition semantics, samples, failures, and digests.
5. Align README numbers and mark evidence current.
6. Run strict validation, publish to `main`, and confirm exact-head CI.

## Risks

- Float total consistency in Polars must match Decimal oracle at the 0.01 boundary.
- The manifest contract must be consumed by #23 before it is promoted into the reusable kit.
- The order fixture is engineering proof, not a universal business contract.
