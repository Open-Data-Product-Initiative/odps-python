"""ODPG graph loading, validation, search, and explorer generation helpers."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple, Union

import jsonschema
import yaml

from open_data_products.results import ValidationResult

from . import _explorer_template

DEFAULT_GRAPH_YAML = Path(__file__).resolve().parent / "data" / "graph" / "graph.yaml"
DEFAULT_SCHEMA_YAML = Path(__file__).resolve().parent / "data" / "schema" / "odpg.yaml"
DEFAULT_OBJECTS_JSONL = (
    Path(__file__).resolve().parent / "data" / "graph" / "objects.jsonl"
)


# --- ODPG relationship model (ODPG spec literals; graphs may add domain-specific types) ---
# Edge `type` values are shown exactly as in YAML (e.g. contributesTo, governedBy, uses).
ODPG_CORE_EDGE_TYPES_ORDERED: Tuple[str, ...] = (
    "uses",
    "supports",
    "contributesTo",
    "measures",
    "tracks",
    "dependsOn",
    "produce",
    "Consumes",
    "governedBy",
    "ownedBy",
    "alignsWith",
    "relatedTo",
    "impacts",
    "derivedFrom",
    "exposes",
    "monitors",
    "identifies",
)

ODPG_EDGE_DESCRIPTIONS: Dict[str, str] = {
    "uses": "A node uses another node as part of execution or operation",
    "supports": "A node supports a business objective",
    "contributesTo": "A node contributes toward an outcome or objective",
    "measures": "A KPI measures an objective or outcome",
    "tracks": "A node tracks or provides KPI-related information",
    "dependsOn": "A node depends on another node",
    "produce": "A node produces data, outputs, or services",
    "Consumes": "A node consumes data, APIs, or outputs",
    "governedBy": "A node is governed by a policy or control",
    "ownedBy": "A node is owned by a person, team, or domain",
    "alignsWith": "A node aligns strategically or semantically with another node",
    "relatedTo": "A generic semantic relationship",
    "impacts": "A node impacts another node",
    "derivedFrom": "A node originates from another node",
    "exposes": "A node exposes an API or interface",
    "monitors": "A node monitors another node",
    "identifies": "A node identifies an opportunity or condition",
}

ODPG_EDGE_DESCRIPTIONS_LOWER: Dict[str, str] = {
    k.lower(): v for k, v in ODPG_EDGE_DESCRIPTIONS.items()
}

ODPG_CORE_EDGE_TYPES_LOWER: FrozenSet[str] = frozenset(
    s.lower() for s in ODPG_CORE_EDGE_TYPES_ORDERED
)

_ODPG_LEGEND_COLOR_BY_LOWER: Dict[str, str] = {
    "uses": "#16a34a",
    "supports": "#ea580c",
    "contributesto": "#0284c7",
    "measures": "#0d9488",
    "tracks": "#14b8a6",
    "dependson": "#6366f1",
    "produce": "#059669",
    "consumes": "#a855f7",
    "governedby": "#db2777",
    "ownedby": "#ca8a04",
    "alignswith": "#f97316",
    "relatedto": "#64748b",
    "impacts": "#dc2626",
    "derivedfrom": "#78716c",
    "exposes": "#7c3aed",
    "monitors": "#0891b2",
    "identifies": "#475569",
}


def load_graph(path: Optional[Union[Path, str]] = None) -> Dict[str, Any]:
    """Load an ODPG graph from YAML."""
    graph_path = Path(path) if path is not None else DEFAULT_GRAPH_YAML
    if not graph_path.is_file():
        raise FileNotFoundError(f"Graph YAML not found: {graph_path}")
    graph = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
    if not isinstance(graph, dict):
        raise ValueError("ODPG graph must contain an object at the document root")
    return graph


load_graph_from_yaml = load_graph


def load_schema(path: Optional[Union[Path, str]] = None) -> Dict[str, Any]:
    """Load ODPG schema YAML from ``path`` or bundled package data."""
    schema_path = Path(path) if path is not None else DEFAULT_SCHEMA_YAML
    with schema_path.open(encoding="utf-8") as handle:
        schema = yaml.safe_load(handle)
    if not isinstance(schema, dict):
        raise ValueError("ODPG schema must contain an object at the document root")
    return schema


def _validate_graph_or_raise(graph: Dict[str, Any]) -> bool:
    required_root_fields = ["schema", "version", "kind", "id", "name", "nodes", "edges"]

    for field in required_root_fields:
        if field not in graph:
            raise ValueError(f"Missing required root field: {field}")

    if graph["kind"] != "DataProductGraph":
        raise ValueError("Invalid kind. Expected: DataProductGraph")

    node_ids = set()

    for node in graph["nodes"]:
        for field in ["id", "type"]:
            if field not in node:
                raise ValueError(f"Node is missing required field: {field}")
        if "$ref" not in node and "ref" not in node:
            raise ValueError("Node is missing required field: $ref")

        if node["id"] in node_ids:
            raise ValueError(f"Duplicate node id found: {node['id']}")

        node_ids.add(node["id"])

    for edge in graph["edges"]:
        for field in ["from", "to", "type", "confidence"]:
            if field not in edge:
                raise ValueError(f"Edge is missing required field: {field}")

        if edge["from"] not in node_ids:
            raise ValueError(f"Edge source does not match any node id: {edge['from']}")

        if edge["to"] not in node_ids:
            raise ValueError(f"Edge target does not match any node id: {edge['to']}")

    return True


def validate_graph(graph: Dict[str, Any]) -> ValidationResult:
    """Validate an ODPG graph document against schema and structural checks."""
    errors = []
    try:
        _validate_graph_or_raise(graph)
    except ValueError as exc:
        errors.append(str(exc))

    schema_data = load_schema()
    jsonschema.Draft202012Validator.check_schema(schema_data)
    validator = jsonschema.Draft202012Validator(schema_data)
    schema_errors = sorted(
        validator.iter_errors(_schema_graph(graph)), key=lambda error: list(error.path)
    )
    for error in schema_errors:
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{location}: {error.message}")

    kind = str(graph.get("kind", "DataProductGraph"))
    return ValidationResult(valid=not errors, spec="odpg", kind=kind, errors=errors)


def _schema_graph(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Return graph copy normalized for ODPG schema validation."""
    normalized = dict(graph)
    normalized_nodes = []
    for node in graph.get("nodes", []):
        if not isinstance(node, dict):
            normalized_nodes.append(node)
            continue
        normalized_node = dict(node)
        if "$ref" not in normalized_node and "ref" in normalized_node:
            normalized_node["$ref"] = normalized_node.pop("ref")
        normalized_nodes.append(normalized_node)
    normalized["nodes"] = normalized_nodes
    return normalized


def _ref_to_display_name(ref: str) -> str:
    base = Path(ref).name
    if base.endswith((".yaml", ".yml")):
        base = base.rsplit(".", 1)[0]
    base = base.replace("-", " ").replace("_", " ")
    return " ".join(w.capitalize() for w in base.split()) if base else ""


def _node_ref(node: Dict[str, Any]) -> str:
    return str(node.get("$ref") or node.get("ref") or "")


def _edge_type_raw(edge: dict) -> str:
    return str(edge.get("type", "")).strip()


def collect_relationship_types(graph: dict) -> List[str]:
    """Types present in the graph: ODPG spec order (camelCase literals), then other types A–Z."""
    seen_lower_to_raw: Dict[str, str] = {}
    for edge in graph.get("edges") or []:
        raw = _edge_type_raw(edge)
        if not raw:
            continue
        lo = raw.lower()
        if lo not in seen_lower_to_raw:
            seen_lower_to_raw[lo] = raw
    ordered_core: List[str] = []
    for spec in ODPG_CORE_EDGE_TYPES_ORDERED:
        lo = spec.lower()
        if lo in seen_lower_to_raw:
            ordered_core.append(seen_lower_to_raw[lo])
    extras = sorted(
        (
            seen_lower_to_raw[lo]
            for lo in seen_lower_to_raw
            if lo not in ODPG_CORE_EDGE_TYPES_LOWER
        ),
        key=str.lower,
    )
    return ordered_core + extras


def _edge_relationship_label(edge: dict) -> str:
    """Edge label exactly as authored in YAML `type` (ODPG stabilization spec)."""
    return _edge_type_raw(edge)


def _edge_vis_tooltip(edge: dict, display: str) -> str:
    lines = [f"Type: {display}", f"Confidence: {edge['confidence']}"]
    desc = ODPG_EDGE_DESCRIPTIONS_LOWER.get(display.lower(), "")
    if desc:
        lines.append(desc)
    return "\n".join(lines)


def _edge_legend_color(type_display: str) -> str:
    return _ODPG_LEGEND_COLOR_BY_LOWER.get(type_display.lower(), "#94a3b8")


def _edge_line_dashed(type_display: str, edge: dict) -> bool:
    if edge.get("dashed") is True:
        return True
    return type_display.lower() == "governedby"


def _build_legend_relationship_html(relationship_types: List[str], graph: dict) -> str:
    edges = graph.get("edges") or []

    def sample_edge(label_raw: str) -> dict:
        lo = label_raw.lower()
        for e in edges:
            if _edge_type_raw(e).lower() == lo:
                return e
        return {}

    blocks: List[str] = []
    for label_raw in relationship_types:
        edge_sample = sample_edge(label_raw)
        color = _edge_legend_color(label_raw)
        dash = (
            ' stroke-dasharray="4 3"'
            if _edge_line_dashed(label_raw, edge_sample)
            else ""
        )
        safe_label = html.escape(label_raw)
        blocks.append(
            f'              <div class="legend-edge-item">\n'
            f'                <svg viewBox="0 0 44 14" width="44" height="14" aria-hidden="true">'
            f'<line x1="2" y1="7" x2="34" y2="7" stroke="{color}" stroke-width="2"{dash}/>'
            f'<polygon points="40,7 32,3 32,11" fill="{color}"/></svg>\n'
            f"                <span>{safe_label}</span>\n"
            f"              </div>"
        )
    if not blocks:
        blocks.append(
            '              <p class="panel-placeholder" style="margin:0;font-size:12px">No edges in graph.</p>'
        )
    return "\n".join(blocks)


def build_html(graph: dict) -> str:
    relationship_types = collect_relationship_types(graph)
    odpg_supported_ordered_json = json.dumps(
        list(ODPG_CORE_EDGE_TYPES_ORDERED), ensure_ascii=False
    )
    odpg_descriptions_json = json.dumps(
        ODPG_EDGE_DESCRIPTIONS_LOWER, ensure_ascii=False
    )
    graph_title = graph.get("name", {}).get(
        "en", graph.get("id", "ODPG Graph Explorer")
    )
    graph_meta = (
        f"{graph.get('id')} · ODPG {graph.get('version')} · {graph.get('kind')}"
    )

    vis_nodes = []
    for node in graph["nodes"]:
        ref = _node_ref(node)
        display_name = _ref_to_display_name(ref)
        vis_nodes.append(
            {
                "id": node["id"],
                "label": node["id"],
                "title": (
                    f"ID: {node['id']}\n" f"Type: {node['type']}\n" f"Ref: {ref}"
                ),
                "group": node["type"],
                "ref": ref,
                "type": node["type"],
                "displayName": display_name,
            }
        )

    vis_edges = []
    for edge in graph["edges"]:
        display = _edge_relationship_label(edge)
        conf = str(edge["confidence"]).lower()
        ec = _edge_legend_color(display)
        vis_edges.append(
            {
                "from": edge["from"],
                "to": edge["to"],
                "label": f"{display}\n({conf})",
                "title": _edge_vis_tooltip(edge, display),
                "arrows": "to",
                "confidence": edge["confidence"],
                "dashes": _edge_line_dashed(display, edge),
                "color": {
                    "color": ec,
                    "highlight": ec,
                    "hover": ec,
                    "inherit": False,
                },
            }
        )

    legend_edges_html = _build_legend_relationship_html(relationship_types, graph)

    return _explorer_template.render_explorer(
        graph_title=graph_title,
        graph_meta=graph_meta,
        relationship_types=relationship_types,
        vis_nodes=vis_nodes,
        vis_edges=vis_edges,
        legend_edges_html=legend_edges_html,
        odpg_supported_ordered_json=odpg_supported_ordered_json,
        odpg_descriptions_json=odpg_descriptions_json,
    )


def load_graph_object_records(
    path: Optional[Union[Path, str]] = None,
) -> List[Dict[str, Any]]:
    """Load ODPG graph object records from JSONL."""
    records_path = Path(path) if path is not None else DEFAULT_OBJECTS_JSONL
    records = []
    with records_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{records_path}:{line_number}: invalid JSONL: {exc}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"{records_path}:{line_number}: record is not an object"
                )
            records.append(record)
    return records


def searchable_text(record: Dict[str, Any]) -> str:
    """Flatten an ODPG graph object record into searchable lowercase text."""
    values = []
    for value in record.values():
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        elif isinstance(value, dict):
            values.extend(str(item) for item in value.values())
        else:
            values.append(str(value))
    return " ".join(values).lower()


def search_graph_objects(
    query: Optional[str] = None,
    *,
    object_id: Optional[str] = None,
    records: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Search bundled ODPG graph object records by keyword or exact object id."""
    source_records = records if records is not None else load_graph_object_records()
    if object_id:
        wanted = object_id.lower()
        return [
            record
            for record in source_records
            if record.get("id", "").lower() == wanted
        ]

    terms = [term.lower() for term in (query or "").split() if term.strip()]
    if not terms:
        return source_records

    return [
        record
        for record in source_records
        if all(term in searchable_text(record) for term in terms)
    ]


def render_graph_object_records(records: List[Dict[str, Any]]) -> str:
    """Render ODPG graph object records as compact text."""
    if not records:
        return "No matching ODPG graph objects found.\n"

    sections = []
    for record in records:
        description = record.get("description") or record.get("purpose", "")
        sections.append(
            "\n".join(
                [
                    f"{record.get('id', '(missing id)')}",
                    f"  Type: {record.get('objectType', '(missing type)')}",
                    f"  Description: {description}",
                ]
            )
        )
    return "\n\n".join(sections) + "\n"


def build_graph_explorer_html(graph: Dict[str, Any]) -> str:
    """Build the standalone ODPG graph explorer HTML document."""
    return build_html(graph)


def generate_graph_explorer(
    graph_yaml: Optional[Union[Path, str]] = None,
    output_file: Union[Path, str] = "graph-explorer.html",
) -> Path:
    """Generate a standalone ODPG graph explorer HTML file."""
    graph = load_graph(graph_yaml)
    result = validate_graph(graph)
    if not result.valid:
        raise ValueError("; ".join(result.errors))

    html_out = build_graph_explorer_html(graph)
    output_path = Path(output_file)
    output_path.write_text(html_out, encoding="utf-8")

    return output_path


def explain_graph(
    graph: Dict[str, Any],
    *,
    path: Union[str, Path] = "(memory)",
) -> str:
    """Render an ODPG graph summary for humans and AI agents."""
    relationship_types = collect_relationship_types(graph)
    node_types = sorted(
        {
            str(node.get("type"))
            for node in graph.get("nodes", [])
            if isinstance(node, dict) and node.get("type")
        }
    )
    name = graph.get("name", {})
    if isinstance(name, dict):
        graph_name = name.get("en", "(unnamed)")
    else:
        graph_name = str(name or "(unnamed)")
    lines = [
        f"File: {path}",
        f"Schema: {graph.get('schema', '(missing)')}",
        f"ODPG version: {graph.get('version', '(missing)')}",
        f"Graph id: {graph.get('id', '(missing)')}",
        f"Graph name: {graph_name}",
        f"Kind: {graph.get('kind', '(missing)')}",
        f"Nodes: {len(graph.get('nodes', []))}",
        f"Edges: {len(graph.get('edges', []))}",
    ]
    if node_types:
        lines.append(f"Node types: {', '.join(node_types)}")
    if relationship_types:
        lines.append(f"Relationship types: {', '.join(relationship_types)}")
    refs = [
        _node_ref(node)
        for node in graph.get("nodes", [])
        if isinstance(node, dict) and _node_ref(node)
    ]
    if refs:
        lines.append(f"Node references: {len(refs)}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate graph-explorer.html from an ODPG graph YAML file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="graph_yaml",
        type=Path,
        default=DEFAULT_GRAPH_YAML,
        metavar="PATH",
        help="Path to graph YAML file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("graph-explorer.html"),
        metavar="PATH",
        help="Output HTML file path",
    )
    args = parser.parse_args()
    generate_graph_explorer(args.graph_yaml, args.output)
