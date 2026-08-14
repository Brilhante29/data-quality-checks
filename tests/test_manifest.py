import json

import pytest
from jsonschema import Draft202012Validator, FormatChecker

pytest.importorskip("polars")
pytest.importorskip("pandera")

from data_quality.application import execute_gate
from data_quality.fixture import generate_fixture
from data_quality.manifest import write_validated_batch_manifest
from data_quality.polars_engine import PolarsPanderaQualityEngine


def test_validated_batch_manifest_matches_shared_schema(tmp_path):
    fixture = generate_fixture(tmp_path / "fixture", rows=1_000)
    accepted = tmp_path / "accepted.csv"
    quarantine = tmp_path / "quarantine.csv"
    manifest_path = tmp_path / "validated-batch.json"
    contract_path = tmp_path / "order-batch-v1.contract.json"
    contract_path.write_text(
        json.dumps({"contract_id": "order-batch-v1"}), encoding="utf-8"
    )
    outcome = execute_gate(
        PolarsPanderaQualityEngine(), fixture.csv_path, accepted, quarantine
    )

    manifest = write_validated_batch_manifest(
        manifest_path=manifest_path,
        dataset_id="orders",
        dataset_version="fixture-42",
        contract_path=contract_path,
        input_path=fixture.csv_path,
        accepted_path=accepted,
        quarantine_path=quarantine,
        outcome=outcome,
    )

    schema = json.loads(
        open("contracts/validated-batch-manifest-v1.schema.json", encoding="utf-8").read()
    )
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)
    assert manifest["quality"]["accepted_rows"] == 950
    assert manifest["quality"]["rejected_rows"] == 50
    assert manifest["artifacts"]["accepted"]["sha256"].startswith("sha256:")


def test_manifest_cannot_overwrite_an_artifact(tmp_path):
    artifact = tmp_path / "same.csv"
    artifact.write_text("value\n", encoding="utf-8")
    contract = tmp_path / "contract.json"
    contract.write_text('{"contract_id":"test"}', encoding="utf-8")

    with pytest.raises(ValueError, match="must not overwrite"):
        write_validated_batch_manifest(
            manifest_path=artifact,
            dataset_id="orders",
            dataset_version="v1",
            contract_path=contract,
            input_path=artifact,
            accepted_path=tmp_path / "accepted.csv",
            quarantine_path=tmp_path / "quarantine.csv",
            outcome=None,
        )
