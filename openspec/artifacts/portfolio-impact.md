# Portfolio Impact: data-quality-checks

## Program

- Program id: `mlops-data-platform`
- Program name: MLOps and Data Platform
- Component pack: `mlops-data-platform`

## System Story

Protects the input side of #21 by failing corrupted batches closed and partitioning readable rows into accepted and reason-coded quarantine artifacts before training or analytics. A validated-batch manifest gives #23 and #22 a versioned artifact boundary without Python imports across repositories.

This repository is not a standalone demo. It is one part of the MLOps and Data Platform system and should produce reusable fixtures, benchmark patterns, and decisions for later repositories.

## Proficiency Signal

- Primary profile: `python`
- Stack profile: `python-ml`
- Stack:
- python-3.12
- pandera-0.32.1
- polars-1.42.1
- docker

## Post Angle

Open with `invalid_row_detection_f1 = 1.0000`, then explain independent truth, exact adapter parity, V2 provenance, and the contract used by downstream feature/drift repositories.
