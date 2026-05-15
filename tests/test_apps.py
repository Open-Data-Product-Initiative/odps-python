"""Tests for sample applications built on top of the SDK."""

import json
import importlib.util
import subprocess
import sys
from pathlib import Path

from tests.test_agent_api import sample_odps_product

INSPECTOR_PATH = Path(__file__).resolve().parents[1] / "apps" / "document_inspector" / "cli.py"
INSPECTOR_SPEC = importlib.util.spec_from_file_location(
    "document_inspector_cli",
    INSPECTOR_PATH,
)
assert INSPECTOR_SPEC is not None
assert INSPECTOR_SPEC.loader is not None
inspector = importlib.util.module_from_spec(INSPECTOR_SPEC)
INSPECTOR_SPEC.loader.exec_module(inspector)


def test_document_inspector_prints_human_report(tmp_path, capsys):
    path = tmp_path / "product.yaml"
    path.write_text(sample_odps_product().to_yaml(), encoding="utf-8")

    assert inspector.main([str(path)]) == 0

    output = capsys.readouterr().out
    assert "ODP Document Inspector" in output
    assert "Spec: odps" in output
    assert "Kind: OpenDataProduct" in output
    assert "Valid: yes" in output
    assert "Agent Ready Product" in output
    assert "References:" in output
    assert "Bundled resources:" in output


def test_document_inspector_prints_json_report(tmp_path, capsys):
    path = tmp_path / "product.yaml"
    path.write_text(sample_odps_product().to_yaml(), encoding="utf-8")

    assert inspector.main([str(path), "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["document"]["path"] == str(path)
    assert payload["validation"]["valid"] is True
    assert payload["validation"]["spec"] == "odps"
    assert "Agent Ready Product" in payload["explanation"]
    assert isinstance(payload["references"], list)
    assert any(resource["id"] == "odpv.terms" for resource in payload["resources"])
    assert all("path" not in resource for resource in payload["resources"])


def test_document_inspector_runs_as_script_from_repo_root():
    completed = subprocess.run(
        [
            sys.executable,
            "apps/document_inspector/cli.py",
            "examples/demo_product.yaml",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "ODP Document Inspector" in completed.stdout
    assert "Spec: odps" in completed.stdout
