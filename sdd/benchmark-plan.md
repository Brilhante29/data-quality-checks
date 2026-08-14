# Benchmark Plan: data-quality-checks

## Primary

- Metric: `invalid_row_detection_f1`
- Unit: ratio
- Command: `docker run --rm data-quality-checks:benchmark benchmark --rows 100000`
- Diagnostic result: `benchmarks/results/summary.json`
- Publication result: `benchmarks/publication/data-quality-v2.json`
- Evidence: three immutable Docker runs plus V2 provenance

## Secondary

Precision, recall, confusion counts, rejected rows percent, exact reason match, end-to-end rows/second, duration, rule counts, and artifact SHA-256 values.

## Protocol

- 100,000 measured rows, seed 42.
- Exactly one injected row every 20 rows.
- Five injected families; quantity rows intentionally carry two reasons.
- One 1,000-row full warm-up.
- Timed path includes read, schema, rules, partition, and writes.
- Three complete runs on one image; publish median/range and preserve raw outputs and failures.
- V2 records `workload.measured_iterations=100000` and `execution.repeat=3`; each aggregate metric retains three samples.
- Provenance binds the source commit, image, application wheel, constraints lock, workload config, and generated fixture.
- Docker parity test compares all 1,000 oracle/optimized outcomes before benchmark.

## Verified Baseline

Executed on 2026-08-14 from source `4ba93edf687077aff5c31e06e1723939d40cdb5e` using image ID sha256:8dfa9feaa462082f8ee28c1e5f0ff43c1a955663c5340c766c4045b48421e1e3:

- 3 runs, 100,000 rows each, fixture seed 42.
- invalid_row_detection_f1: 1.0000; precision 1.0000; recall 1.0000.
- Rejected rows: 5.00%; exact reason match: 1.0000.
- Throughput median: 617,445.89 rows/s; range: 547,138.44-891,838.07 rows/s.
- Duration median: 0.161958 s; range: 0.112128-0.182769 s.
- All runs reported zero failures and identical fixture, accepted-output, and quarantine-output hashes.
- Raw files: benchmarks/results/run-1.json, run-2.json, run-3.json.
- V2 publication artifact: benchmarks/publication/data-quality-v2.json; zero failures, false positives, and false negatives.

## Why F1

The 5% rejected ratio is fixture prevalence. F1 proves the gate found injected defects without quarantining valid rows. Exact reason match proves it found the right causes, including multi-rule rows.

## Gates

Publication regeneration must pass: no missing truth, duplicate row IDs, unaccounted rows, changed fixture hash, parity mismatch, hidden failure, unrecorded image/wheel/lock digest, or README number without current evidence.
