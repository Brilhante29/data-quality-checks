# Spec: data-quality-checks

## Number

#26

## Claim

One local-first Docker command validates a strict order-batch structure, quarantines row-rule violations with reason IDs, proves optimized/reference parity, and measures invalid-row detection F1 plus full-gate throughput.

## Problem

A rejected-row percentage can be made impressive by changing the fixture. The portfolio needs a quality gate whose truth exists before validation, whose false positives are measurable, and whose accepted/quarantine outputs account for every readable row.

## Input Contract

Exact ordered columns:

`row_id, order_id, customer_id, quantity, unit_price, total_amount, currency, status`.

Unreadable structure, scalar types, or duplicate row identifiers fail the batch. Row policy checks identifiers, customer, quantity, unit price, currency, status, and amount consistency.

## Outputs

- Accepted CSV with unchanged source columns.
- Quarantine CSV with source columns plus ordered `_reasons`.
- Benchmark JSON with confusion counts, F1, rejected percentage, reason exact match, throughput, hashes, versions, environment, and failures.
- Nonzero failure JSON for exceptions.

## Fixture Truth

Seed 42 creates deterministic valid orders and injects one invalid row every 20 rows across five defect families. Truth records input SHA-256, invalid row IDs, and all expected reasons before validation.

## In Scope

- Eager local CSV validation.
- Batch-fatal structural contract.
- Quarantinable row rules.
- Reference/optimized engine parity.
- Accepted and quarantine artifacts.
- Reproducible 100,000-row benchmark.

## Out Of Scope

- Data docs or hosted suite operations.
- SQL analytics or persistent storage.
- Distributed Spark execution.
- Streaming/windowing.
- Airflow, MLflow, API servers, brokers, cloud, dashboards, and remediation.

## Acceptance

- Every readable row is accepted or quarantined exactly once.
- Reason IDs are bounded, ordered, and machine-readable.
- Optimized and reference engines return identical outcomes.
- Benchmark scores all injected row/reason truth.
- Default Docker path is non-root, offline, and secret-free.
- README uses only current committed Docker evidence.
