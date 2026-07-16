import csv
import json

import pytest

from data_quality.application import execute_gate
from data_quality.fixture import generate_fixture
from data_quality.reference_engine import ReferenceQualityEngine


def test_fixture_is_deterministic_and_injects_exact_five_percent(tmp_path):
    first = generate_fixture(tmp_path / "first", rows=100, seed=42)
    second = generate_fixture(tmp_path / "second", rows=100, seed=42)

    assert first.sha256 == second.sha256
    assert first.truth == second.truth
    assert len(first.truth) == 5
    persisted = json.loads(first.truth_path.read_text(encoding="utf-8"))
    assert persisted["csv_sha256"] == first.sha256


def test_reference_engine_quarantines_exact_truth_with_reasons(tmp_path):
    fixture = generate_fixture(tmp_path / "fixture", rows=100, seed=42)
    accepted = tmp_path / "accepted.csv"
    quarantine = tmp_path / "quarantine.csv"

    outcome = execute_gate(
        ReferenceQualityEngine(),
        fixture.csv_path,
        accepted,
        quarantine,
    )

    assert outcome.accepted_rows == 95
    assert {item.row_id: item.reasons for item in outcome.rejections} == fixture.truth
    assert len(list(csv.DictReader(accepted.open(encoding="utf-8")))) == 95
    quarantined = list(csv.DictReader(quarantine.open(encoding="utf-8")))
    assert len(quarantined) == 5
    assert all(row["_reasons"] for row in quarantined)


def test_reference_engine_fails_closed_on_schema_scalar_or_duplicate(tmp_path):
    fixture = generate_fixture(tmp_path / "fixture", rows=20)
    content = fixture.csv_path.read_text(encoding="utf-8")

    wrong_header = tmp_path / "wrong.csv"
    wrong_header.write_text(content.replace("row_id", "id", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="columns"):
        execute_gate(
            ReferenceQualityEngine(),
            wrong_header,
            tmp_path / "a.csv",
            tmp_path / "q.csv",
        )

    duplicate = tmp_path / "duplicate.csv"
    lines = content.splitlines()
    fields = lines[2].split(",")
    fields[0] = "0"
    lines[2] = ",".join(fields)
    duplicate.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        execute_gate(
            ReferenceQualityEngine(),
            duplicate,
            tmp_path / "a2.csv",
            tmp_path / "q2.csv",
        )


def test_application_protects_input_and_output_paths(tmp_path):
    fixture = generate_fixture(tmp_path / "fixture", rows=20)
    with pytest.raises(ValueError, match="overwrite"):
        execute_gate(
            ReferenceQualityEngine(),
            fixture.csv_path,
            fixture.csv_path,
            tmp_path / "q.csv",
        )
    with pytest.raises(ValueError, match="differ"):
        execute_gate(
            ReferenceQualityEngine(),
            fixture.csv_path,
            tmp_path / "same.csv",
            tmp_path / "same.csv",
        )


def test_fixture_rejects_too_few_rows(tmp_path):
    with pytest.raises(ValueError, match="at least 20"):
        generate_fixture(tmp_path / "bad", rows=19)
