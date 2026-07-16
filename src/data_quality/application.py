from __future__ import annotations

from pathlib import Path
from typing import Protocol

from data_quality.domain import QualityOutcome


class QualityEngine(Protocol):
    def validate(
        self,
        input_path: Path,
        accepted_path: Path,
        quarantine_path: Path,
    ) -> QualityOutcome: ...


def execute_gate(
    engine: QualityEngine,
    input_path: Path,
    accepted_path: Path,
    quarantine_path: Path,
) -> QualityOutcome:
    if input_path.resolve() in {
        accepted_path.resolve(),
        quarantine_path.resolve(),
    }:
        raise ValueError("output paths must not overwrite the input")
    if accepted_path.resolve() == quarantine_path.resolve():
        raise ValueError("accepted and quarantine paths must differ")
    accepted_path.parent.mkdir(parents=True, exist_ok=True)
    quarantine_path.parent.mkdir(parents=True, exist_ok=True)
    return engine.validate(input_path, accepted_path, quarantine_path)
