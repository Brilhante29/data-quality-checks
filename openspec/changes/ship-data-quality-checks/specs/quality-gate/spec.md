# Quality Gate Requirements

## Structural Gate

The system SHALL require exact ordered columns, exact scalar types, and unique row IDs. Structural failure SHALL stop the batch and return nonzero.

## Row Partition

Every readable row SHALL appear exactly once in accepted or quarantine output. Quarantine SHALL include ordered bounded reason IDs.

## Engine Parity

The Pandera/Polars implementation SHALL produce the same `QualityOutcome` as the standard-library reference engine for deterministic parity fixtures.

## Benchmark Truth

The generator SHALL persist seed, input SHA-256, invalid row IDs, and expected reason IDs before validation. The benchmark SHALL report confusion, F1, rejected percentage, exact reason match, throughput, output hashes, environment, and failures.

## Publication

Evidence SHALL remain pending until at least three full runs share one image ID and benchmark signature and strict validation passes.
