import pytest

pytest.importorskip("polars")
pytest.importorskip("pandera")

from data_quality.application import execute_gate
from data_quality.fixture import generate_fixture
from data_quality.polars_engine import PolarsPanderaQualityEngine
from data_quality.reference_engine import ReferenceQualityEngine


def test_polars_engine_is_lsp_equivalent_to_reference_engine(tmp_path):
    fixture = generate_fixture(tmp_path / "fixture", rows=1_000)
    reference = execute_gate(
        ReferenceQualityEngine(),
        fixture.csv_path,
        tmp_path / "reference-accepted.csv",
        tmp_path / "reference-quarantine.csv",
    )
    optimized = execute_gate(
        PolarsPanderaQualityEngine(),
        fixture.csv_path,
        tmp_path / "polars-accepted.csv",
        tmp_path / "polars-quarantine.csv",
    )

    assert optimized == reference
    assert {item.row_id: item.reasons for item in optimized.rejections} == fixture.truth
