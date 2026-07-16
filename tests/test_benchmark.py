import pytest

pytest.importorskip("polars")
pytest.importorskip("pandera")

from data_quality.benchmark import run_benchmark


def test_benchmark_proves_detection_and_writes_result(tmp_path):
    output = tmp_path / "summary.json"

    result = run_benchmark(output, rows=1_000, command="test")

    assert result["metric"] == "invalid_row_detection_f1"
    assert result["value"] == 1.0
    assert result["summary"]["rejected_rows_percent"] == 5.0
    assert result["summary"]["reason_exact_match_rate"] == 1.0
    assert result["summary"]["throughput_rows_per_second"] > 0
    assert output.is_file()


def test_benchmark_rejects_small_input():
    with pytest.raises(ValueError, match="at least 1000"):
        run_benchmark(None, rows=999)
