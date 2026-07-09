# #26 data-quality-checks

**Status:** scaffold

**Proves:** validacao objetiva de dados.

**Benchmark target:** rejected_rows_percent.

**Stack:** python, pandera, duckdb, polars, docker.

## Next milestone

Implement the smallest Docker-runnable version and produce the first JSON benchmark under enchmarks/results/.

## Run

`ash
docker build -t data-quality-checks .
docker run --rm data-quality-checks
`

## Benchmark

`ash
docker run --rm data-quality-checks benchmark
`

| Metric | Value | Unit |
|---|---:|---|
| rejected_rows_percent | pending | pending |

## Architecture

Defined in sdd/spec.md before implementation.

## References

See REFERENCES.md.