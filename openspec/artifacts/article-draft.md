# #26 data-quality-checks: invalid_row_detection_f1 = pending

One local-first Docker command applies a strict structural contract, quarantines rule violations with exact reason IDs, proves Polars/Pandera parity against a Python oracle, and scores invalid-row detection F1, rejected percentage, and full-gate throughput.

This repository belongs to the MLOps and Data Platform program. Its job is narrow: prove the measurable claim through the selected component pack before adding unrelated infrastructure or features.

The benchmark is the proof. invalid_row_detection_f1 = pending.  The result is stored in `benchmarks/results/summary.json` and can be reproduced from the Docker/local path.

The important architecture decision is pipeline. The dominant force is ordered gating: load, validate structure, evaluate row policy, partition outputs, score against independent truth, and emit benchmark evidence.

The default path stays local-first. The project uses python-ml, exposes cli, uses messaging mode `none`, and stores data with `none`. The dependency rule is explicit: Pandera/Polars and CSV adapters depend on domain rule IDs, outcomes, and the QualityEngine port; domain and application policy never depend on DataFrame frameworks.

The rejected work matters as much as the implemented work. Anything that does not improve the benchmark stays out of the first version.

Post angle: start with the number, show the architecture boundary, then explain which future adapter can be added without changing the core use cases.
