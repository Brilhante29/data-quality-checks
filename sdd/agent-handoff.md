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

- Domain, fixture, oracle, optimized adapter, benchmark, CLI, tests, Docker, README, SDD, and references are staged.
- Host: 19 tests pass; Pandera/Polars parity and benchmark tests are correctly skipped because those packages are unavailable.
- Python 3.12 syntax passes.
- Kit: data-quality skills/docs, component pack, catalog, and Python profile are staged and validated.
- Docker, exact adapter APIs, coverage, transitive freeze, three runs, Desktop sync, GitHub publication, and CI remain pending.

## Docker Order

1. Build and record image ID/size.
2. Freeze transitive dependencies and rebuild.
3. Run Ruff and all tests; confirm no skips in Polars/Pandera modules.
4. Require at least 90% focused coverage.
5. Run 1,000-row oracle/optimized parity.
6. Run one short benchmark and inspect accepted/quarantine outputs.
7. Run three 100,000-row benchmarks on one image.
8. Aggregate without dropping failures; update README and evidence status.
9. Run strict validator.
10. Publish kit first, synchronize its exact commit, publish #26, and confirm green CI.

## Risks

- Pandera/Polars current API has not run locally.
- Float total consistency in Polars must match Decimal oracle at the 0.01 boundary.
- Transitive dependencies are not frozen.
- The order fixture is engineering proof, not a universal business contract.
