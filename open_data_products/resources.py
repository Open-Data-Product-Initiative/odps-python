"""Bundled resource registry for the Open Data Products SDK."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .results import Resource

_PACKAGE_ROOT = Path(__file__).resolve().parent

_RESOURCES = [
    Resource(
        id="odpc.schema.yaml",
        spec="odpc",
        type="schema",
        path=str(_PACKAGE_ROOT / "odpc" / "data" / "schema" / "odpc.yaml"),
        description="Bundled ODPC catalog schema in YAML format.",
    ),
    Resource(
        id="odpc.schema.json",
        spec="odpc",
        type="schema",
        path=str(_PACKAGE_ROOT / "odpc" / "data" / "schema" / "odpc.json"),
        description="Bundled ODPC catalog schema in JSON format.",
    ),
    Resource(
        id="odpc.objects",
        spec="odpc",
        type="jsonl",
        path=str(_PACKAGE_ROOT / "odpc" / "data" / "catalog" / "objects.jsonl"),
        description="Bundled ODPC object guidance records.",
    ),
    Resource(
        id="odpg.schema.yaml",
        spec="odpg",
        type="schema",
        path=str(_PACKAGE_ROOT / "odpg" / "data" / "schema" / "odpg.yaml"),
        description="Bundled ODPG graph schema in YAML format.",
    ),
    Resource(
        id="odpg.schema.json",
        spec="odpg",
        type="schema",
        path=str(_PACKAGE_ROOT / "odpg" / "data" / "schema" / "odpg.json"),
        description="Bundled ODPG graph schema in JSON format.",
    ),
    Resource(
        id="odpg.graph",
        spec="odpg",
        type="example",
        path=str(_PACKAGE_ROOT / "odpg" / "data" / "graph" / "graph.yaml"),
        description="Bundled ODPG example graph used by graph explorer helpers.",
    ),
    Resource(
        id="odpg.objects",
        spec="odpg",
        type="jsonl",
        path=str(_PACKAGE_ROOT / "odpg" / "data" / "graph" / "objects.jsonl"),
        description="Bundled ODPG graph object guidance records.",
    ),
    Resource(
        id="odpv.vocabulary",
        spec="odpv",
        type="vocabulary",
        path=str(_PACKAGE_ROOT / "odpv" / "data" / "vocab" / "odpv.yaml"),
        description="Bundled canonical ODPV vocabulary YAML.",
    ),
    Resource(
        id="odpv.terms",
        spec="odpv",
        type="jsonl",
        path=str(_PACKAGE_ROOT / "odpv" / "data" / "vocab" / "terms.jsonl"),
        description="Bundled ODPV term records for retrieval and search.",
    ),
]


def list_resources() -> List[Resource]:
    """List bundled SDK resources for tools and AI agents."""
    return list(_RESOURCES)


def get_resource(resource_id: str) -> Resource:
    """Return a bundled SDK resource by id."""
    for resource in _RESOURCES:
        if resource.id == resource_id:
            return resource
    raise KeyError(f"Unknown Open Data Products resource: {resource_id}")
