"""Open Data Product Graph (ODPG) namespace."""

from .graph import (
    build_graph_explorer_html,
    collect_relationship_types,
    explain_graph,
    generate_graph_explorer,
    load_graph,
    load_graph_object_records,
    load_schema,
    render_graph_object_records,
    search_graph_objects,
    validate_graph,
)

SPEC_ID = "odpg"
SPEC_NAME = "Open Data Product Graph"

__all__ = [
    "SPEC_ID",
    "SPEC_NAME",
    "build_graph_explorer_html",
    "collect_relationship_types",
    "explain_graph",
    "generate_graph_explorer",
    "load_graph",
    "load_graph_object_records",
    "load_schema",
    "render_graph_object_records",
    "search_graph_objects",
    "validate_graph",
]
