# Architecture Record: data-quality-checks

## Decision

- Architecture: `pipeline`
- Stack profile: `python-ml`
- API style: `cli`
- Messaging: `none`
- Database/runtime: `none` / `Single non-root Python 3.12.13 container pinned by OCI digest; eager local DataFrame validation and deterministic CPU benchmark.`

## Reason

The dominant force is ordered gating: load, validate structure, evaluate row policy, partition outputs, score against independent truth, and emit benchmark evidence.

## Dependency Direction

Pandera/Polars and CSV adapters depend on domain rule IDs, outcomes, and the QualityEngine port; domain and application policy never depend on DataFrame frameworks.

## Boundaries

- deterministic fixture and injected truth
- immutable order record and row policy
- quality engine application port
- standard-library reference engine
- Pandera structural schema
- Polars vectorized rule and partition adapter
- JSON Schema validated-batch artifact boundary
- benchmark scoring and CLI

## Library Policy

Pandera owns exact structural DataFrame validation, Polars owns vectorized row predicates and output partitioning, JSON Schema owns the cross-repository artifact boundary, and the standard-library reference engine is the LSP oracle. DuckDB and Great Expectations are rejected because SQL persistence and suite operations are not measured.

## Principle Check

- SRP: keep benchmark, API, use cases, and adapters separate.
- OCP: new providers must be adapters, not domain rewrites.
- LSP: replacement providers must preserve observable behavior.
- ISP: ports stay narrow.
- DIP: application depends on behavior, not infrastructure.
- KISS/YAGNI: leave out anything that does not improve the benchmark.
