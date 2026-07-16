# Design: ship data-quality-checks

## Flow

```text
CSV -> eager Pandera structure -> Polars rules -> accepted/quarantine
Python oracle -------------------------------> parity
injected truth + output ---------------------> F1/reason/throughput evidence
```

## Invariants

- Structural corruption fails the batch.
- Every readable row appears in exactly one output.
- Quarantine retains source identity and ordered bounded reasons.
- Truth is generated before validation.
- Optimized and oracle outcomes are identical.
- Rejected prevalence is not the primary quality claim.
- Evidence remains pending until same-image Docker aggregation.

## Rejected Complexity

No DuckDB, Great Expectations project, Spark, API, broker, database, cloud, scheduler, registry, dashboard, or remediation enters this change.
