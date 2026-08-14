# Benchmark Proof: data-quality-checks

## Primary Metric

- Metric: `invalid_row_detection_f1`
- Unit: `ratio`
- Result: `invalid_row_detection_f1 = 1.0000`
- Diagnostic result: `benchmarks/results/summary.json`
- Publication result: `benchmarks/publication/data-quality-v2.json`

## Command

    ./tools/benchmark.ps1

## Evidence

Three Docker repetitions each measure 100,000 labeled rows after a 1,000-row warm-up. V2 retains every metric sample and binds the source commit, workload, fixture, constraints lock, image, and application wheel.

The README/post number must come from the committed V2 benchmark JSON, not from manual text.
