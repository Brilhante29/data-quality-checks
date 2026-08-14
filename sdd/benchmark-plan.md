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

Executed on 2026-08-14 from source `2ceee2e3dcbce6d8abeb33492113d02eb7dd1f20` using image ID sha256:c7c88eb12716707f65479627fc9a9b55fe60d86fbadd68e0194fb427176f27fc:

- 3 runs, 100,000 rows each, fixture seed 42.
- invalid_row_detection_f1: 1.0000; precision 1.0000; recall 1.0000.
- Rejected rows: 5.00%; exact reason match: 1.0000.
- Throughput median: 717,607.98 rows/s; range: 684,860.81-791,482.53 rows/s.
- Duration median: 0.139352 s; range: 0.126345-0.146015 s.
- All runs reported zero failures and identical fixture, accepted-output, and quarantine-output hashes.
- Raw files: benchmarks/results/run-1.json, run-2.json, run-3.json.
- V2 publication artifact: benchmarks/publication/data-quality-v2.json; zero failures, false positives, and false negatives.

## Why F1

The 5% rejected ratio is fixture prevalence. F1 proves the gate found injected defects without quarantining valid rows. Exact reason match proves it found the right causes, including multi-rule rows.

## Gates

Publication regeneration must pass: no missing truth, duplicate row IDs, unaccounted rows, changed fixture hash, parity mismatch, hidden failure, unrecorded image/wheel/lock digest, or README number without current evidence.
