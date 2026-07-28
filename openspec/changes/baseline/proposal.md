# Change Proposal: baseline

Project: `data-quality-checks` (#26)

## Intent

One local-first Docker command applies a strict structural contract, quarantines rule violations with exact reason IDs, proves Polars/Pandera parity against a Python oracle, and scores invalid-row detection F1, rejected percentage, and full-gate throughput.

## Why This Change Exists

Describe the smallest change that improves the measurable claim or removes a
known portfolio risk.

## Scope

- In scope: Polars and Pandera data quality validation, invalid row quarantine, and local-first benchmark reproducibility.
- Out of scope: paid credentials, unrelated infrastructure, and unmeasured features.

## Portfolio Impact

Program: `mlops-data-platform`

This change should produce evidence, fixtures, decisions, or components that
can be reused by sibling repositories without moving project-specific behavior
into the kit.

## Acceptance Signal

The benchmark in `project.yaml` remains reproducible and its result is recorded
in `benchmarks/results/`.
