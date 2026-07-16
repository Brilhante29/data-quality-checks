# Benchmark Plan: data-quality-checks

## Primary

- Metric: `invalid_row_detection_f1`
- Unit: ratio
- Command: `docker run --rm data-quality-checks`
- Result: `benchmarks/results/summary.json`
- Evidence: pending immutable Docker runs

## Secondary

Precision, recall, confusion counts, rejected rows percent, exact reason match, end-to-end rows/second, duration, rule counts, and artifact SHA-256 values.

## Protocol

- 100,000 measured rows, seed 42.
- Exactly one injected row every 20 rows.
- Five injected families; quantity rows intentionally carry two reasons.
- One 1,000-row full warm-up.
- Timed path includes read, schema, rules, partition, and writes.
- Three complete runs on one image; publish median/range and preserve failures.
- Docker parity test compares all 1,000 oracle/optimized outcomes before benchmark.

## Why F1

The 5% rejected ratio is fixture prevalence. F1 proves the gate found injected defects without quarantining valid rows. Exact reason match proves it found the right causes, including multi-rule rows.

## Gates

No missing truth, duplicate row IDs, unaccounted rows, changed fixture hash, parity mismatch, hidden failure, unrecorded image ID, or README number without current summary.
