# Proposal: ship data-quality-checks

## Why

The MLOps system needs a strict ingestion gate before training. A useful proof must preserve quarantine and measure false positives/misses against known defects.

## What Changes

- Add exact order-batch structural validation.
- Add seven named row rules and accepted/quarantine outputs.
- Add a standard-library oracle and Pandera/Polars measured engine.
- Add deterministic defect truth, multi-rule rows, F1/reason/throughput benchmark, Docker, tests, and CI.
- Patch reusable data-quality and semantic aggregation guidance into the kit.

## Impact

#26 becomes the input guard for #21 and establishes reusable proof conventions without importing downstream code.
