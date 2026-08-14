import importlib.util
from pathlib import Path


def load_producer():
    path = Path("tools/build_v2_evidence.py")
    spec = importlib.util.spec_from_file_location("build_v2_evidence", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_effective_workload_uses_executed_smoke_size():
    producer = load_producer()
    template = {
        "measured_rows_per_repetition": 100_000,
        "repetitions": 3,
        "fixture_seed": 42,
    }

    smoke = producer.effective_workload(template, rows=1_000, repetitions=3)

    assert smoke["measured_rows_per_repetition"] == 1_000
    assert smoke["repetitions"] == 3
    assert template["measured_rows_per_repetition"] == 100_000
