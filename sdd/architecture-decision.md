# Architecture Decision: data-quality-checks

## Status

Accepted for implementation; exact adapter runtime evidence pending.

## Decision

Use a pipeline architecture with a narrow `QualityEngine` port:

```text
CSV -> structural gate -> row rules -> accepted/quarantine -> truth scoring -> evidence
```

The domain owns records, rule IDs, thresholds, outcomes, and scoring. A standard-library reference engine and a Pandera/Polars engine implement the same port.

## SOLID And Simplicity

- **SRP:** structure, policy, engines, fixture, scoring, CLI, and benchmark change independently.
- **OCP:** another DataFrame engine can implement `QualityEngine` without changing scoring or public semantics.
- **LSP:** parity tests require identical rejected IDs, ordered reasons, counts, and accepted rows.
- **ISP:** the engine port has one file-to-partitions operation.
- **DIP:** application flow depends on `QualityOutcome`, not Pandera or Polars.
- **KISS:** one eager batch and seven named rules make the claim auditable.
- **YAGNI:** no API, broker, DB, scheduler, cloud, or auto-remediation.
- **DRY:** rule IDs/constants are shared; optimized expression duplication is guarded by oracle parity.

## Why Pipeline

Correct order dominates: no row scoring before structural trust, no dropping before partitioning, no public metric before independent truth, and no publication before current evidence.

## Rejected

- MVC/layered: no controller/repository problem.
- Hexagonal as primary label: the port is real, but ordered transforms dominate.
- Event-driven: no stream or delivery semantics.
- DuckDB: no SQL or persistence.
- Great Expectations: no suites, checkpoints, stores, or data docs claim.

## OpenSpec Self-Challenge

| Question | Answer |
|---|---|
| Why two engines? | The readable oracle prevents vectorized optimization from silently changing policy and provides tested LSP evidence. |
| Is duplicated expression logic acceptable? | Only while exact parity is mandatory; the domain remains the semantic source. |
| Why is rejected percentage secondary? | It is fixed by injected prevalence and says nothing about false positives or misses. |
| Does Pandera validate data-level checks? | The project uses an eager DataFrame; no LazyFrame data-level claim is made. |
| What would change the architecture? | A measured stream, remote service, SQL join, or distributed-volume requirement. |
