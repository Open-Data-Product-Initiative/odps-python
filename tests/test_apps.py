"""Tests for sample applications built on top of the SDK."""

import json
import importlib.util
import subprocess
import sys
from pathlib import Path

from tests.test_agent_api import sample_odps_product

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_app_module(name, relative_path):
    """Load a standalone sample app module by file path."""
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inspector = load_app_module(
    "document_inspector_cli",
    Path("apps") / "document_inspector" / "cli.py",
)
vocabulary_finder = load_app_module(
    "vocabulary_finder_cli",
    Path("apps") / "vocabulary_finder" / "cli.py",
)


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


def test_vocabulary_finder_prints_human_matches(capsys):
    assert vocabulary_finder.main(
        ["customer churn reusable data offering", "--limit", "2"]
    ) == 0

    output = capsys.readouterr().out
    assert "ODPV Vocabulary Finder" in output
    assert "Query: customer churn reusable data offering" in output
    assert "Matches: 2" in output
    assert "DataProduct" in output
    assert "Definition:" in output
    assert "Related terms:" in output


def test_vocabulary_finder_prints_json_matches(capsys):
    assert (
        vocabulary_finder.main(["governance policy risk", "--limit", "3", "--json"])
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["query"] == "governance policy risk"
    assert payload["limit"] == 3
    assert payload["count"] >= 1
    assert payload["matches"][0]["id"]
    assert payload["matches"][0]["uri"].startswith("https://")


def test_vocabulary_finder_returns_one_when_no_matches(capsys):
    assert vocabulary_finder.main(["zzznomatchterm", "--json"]) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 0
    assert payload["matches"] == []


def test_vocabulary_finder_runs_as_script_from_repo_root():
    completed = subprocess.run(
        [
            sys.executable,
            "apps/vocabulary_finder/cli.py",
            "customer churn reusable data offering",
            "--limit",
            "1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "ODPV Vocabulary Finder" in completed.stdout
    assert "DataProduct" in completed.stdout
