# Benchmark Plan: data-quality-checks

## Primary

- Metric: `invalid_row_detection_f1`
- Unit: ratio
- Command: `docker run --rm data-quality-checks:benchmark benchmark --rows 100000`
- Result: `benchmarks/results/summary.json`
- Evidence: current; three immutable Docker runs plus raw outputs

## Secondary

Precision, recall, confusion counts, rejected rows percent, exact reason match, end-to-end rows/second, duration, rule counts, and artifact SHA-256 values.

## Protocol

- 100,000 measured rows, seed 42.
- Exactly one injected row every 20 rows.
- Five injected families; quantity rows intentionally carry two reasons.
- One 1,000-row full warm-up.
- Timed path includes read, schema, rules, partition, and writes.
- Three complete runs on one image; publish median/range and preserve raw outputs and failures.
- Docker parity test compares all 1,000 oracle/optimized outcomes before benchmark.

## Verified Baseline

Executed on 2026-07-16 using image ID sha256:eae434750a1ae276f8cf17ccf1806c7c8f44c51218e5f9437625ebc0c3017127:

- 3 runs, 100,000 rows each, fixture seed 42.
- invalid_row_detection_f1: 1.0000; precision 1.0000; recall 1.0000.
- Rejected rows: 5.00%; exact reason match: 1.0000.
- Throughput median: 360,303.53 rows/s; range: 351,839.30-407,935.11 rows/s.
- Duration median: 0.277544 s; range: 0.245137-0.284221 s.
- All runs reported zero failures and identical fixture, accepted-output, and quarantine-output hashes.
- Raw files: benchmarks/results/run-1.json, run-2.json, run-3.json.

## Why F1

The 5% rejected ratio is fixture prevalence. F1 proves the gate found injected defects without quarantining valid rows. Exact reason match proves it found the right causes, including multi-rule rows.

## Gates

All current gates passed: no missing truth, duplicate row IDs, unaccounted rows, changed fixture hash, parity mismatch, hidden failure, unrecorded image ID, or README number without current summary.
