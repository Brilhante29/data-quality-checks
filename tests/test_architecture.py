import ast
from pathlib import Path

FORBIDDEN = {
    "pandera",
    "polars",
    "duckdb",
    "great_expectations",
    "fastapi",
    "airflow",
    "mlflow",
    "boto3",
}


def imports(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_domain_application_and_reference_engine_are_framework_independent():
    for path in (
        "src/data_quality/domain.py",
        "src/data_quality/application.py",
        "src/data_quality/reference_engine.py",
    ):
        assert not (imports(path) & FORBIDDEN)
