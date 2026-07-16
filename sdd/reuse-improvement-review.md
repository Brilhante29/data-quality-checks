# Reuse Improvement Review: data-quality-checks

## Trigger

The old kit catalog described #26 with Pandera, DuckDB, Polars, and rejected percentage. Problem-first analysis showed DuckDB had no role and rejected percentage measured fixture prevalence rather than validator quality.

## Kit Patches

- Added `python-data-quality` skills for Codex and Claude.
- Added `docs/data-quality.md`.
- Updated MLOps pack with F1, throughput, defect truth, quarantine, and parity.
- Updated Python profile with structural/row separation and LazyFrame depth rule.
- Updated #26 catalog stack and primary metric.
- Added kit validator checks for every new reusable artifact.

## Kept Local

Order columns, seven rules, thresholds, fixture seeds, five defect families, output names, Polars expressions, benchmark size, and CLI remain project-specific.

## OpenSpec Self-Challenge

| Question | Answer |
|---|---|
| Why not add a generic rule DSL? | One project has not justified maintaining a second language; canonical Python policy plus parity is simpler. |
| Why is no report schema added? | The shared benchmark schema already governs public evidence; add a quality-report contract only when a second consumer needs it. |
| Did a desired skill disappear? | No. DuckDB remains available for #23 or analytics where SQL behavior is measured. |
| Is the oracle overengineering? | No. It catches semantic drift in the optimized adapter and is exercised as LSP proof. |

## Final Gate

- [x] Reusable improvements were patched or recorded.
- [x] Project-specific implementation was not moved into the kit.
- [x] Validation reflects labeled truth, parity, and primary metric improvements.

## Verdict

`patch-required-and-applied` for planning and static validation. Runtime evidence and publication remain pending.
