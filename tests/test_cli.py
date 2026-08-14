import json

import pytest

pytest.importorskip("polars")
pytest.importorskip("pandera")

from data_quality.cli import run
from data_quality.fixture import generate_fixture


def test_cli_gate_and_benchmark_paths(tmp_path, capsys):
    fixture = generate_fixture(tmp_path / "fixture", rows=1_000)
    accepted = tmp_path / "accepted.csv"
    quarantine = tmp_path / "quarantine.csv"
    manifest = tmp_path / "validated-batch.json"

    assert (
        run(
            [
                "gate",
                str(fixture.csv_path),
                "--accepted",
                str(accepted),
                "--quarantine",
                str(quarantine),
                "--manifest",
                str(manifest),
                "--contract",
                "contracts/order-batch-v1.contract.json",
            ]
        )
        == 0
    )
    gate_result = json.loads(capsys.readouterr().out)
    assert gate_result["quality"]["rejected_rows"] == 50
    assert gate_result["contract"]["id"] == "order-batch-v1"
    assert manifest.is_file()

    output = tmp_path / "summary.json"
    assert run(["benchmark", "--rows", "1000", "--output", str(output)]) == 0
    benchmark_result = json.loads(capsys.readouterr().out)
    assert benchmark_result["value"] == 1.0
