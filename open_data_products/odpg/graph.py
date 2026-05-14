"""ODPG graph loading, validation, search, and explorer generation helpers."""

from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

DEFAULT_GRAPH_YAML = Path(__file__).resolve().parent / "data" / "graph" / "graph.yaml"
DEFAULT_SCHEMA_YAML = Path(__file__).resolve().parent / "data" / "schema" / "odpg.yaml"
DEFAULT_OBJECTS_JSONL = (
    Path(__file__).resolve().parent / "data" / "graph" / "objects.jsonl"
)


@dataclass(frozen=True)
class GraphValidationResult:
    """Result from validating an ODPG graph document."""

    valid: bool
    errors: List[str]


# --- ODPG relationship model (ODPG spec literals; graphs may add domain-specific types) ---
# Edge `type` values are shown exactly as in YAML (e.g. contributesTo, governedBy, uses).
ODPG_CORE_EDGE_TYPES_ORDERED: tuple[str, ...] = (
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

ODPG_EDGE_DESCRIPTIONS: dict[str, str] = {
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

ODPG_EDGE_DESCRIPTIONS_LOWER: dict[str, str] = {
    k.lower(): v for k, v in ODPG_EDGE_DESCRIPTIONS.items()
}

ODPG_CORE_EDGE_TYPES_LOWER: frozenset[str] = frozenset(
    s.lower() for s in ODPG_CORE_EDGE_TYPES_ORDERED
)

_ODPG_LEGEND_COLOR_BY_LOWER: dict[str, str] = {
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
        for field in ["id", "type", "ref"]:
            if field not in node:
                raise ValueError(f"Node is missing required field: {field}")

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


def validate_graph(graph: Dict[str, Any]) -> GraphValidationResult:
    """Validate an ODPG graph document using the source script checks."""
    try:
        _validate_graph_or_raise(graph)
    except ValueError as exc:
        return GraphValidationResult(valid=False, errors=[str(exc)])
    return GraphValidationResult(valid=True, errors=[])


def _ref_to_display_name(ref: str) -> str:
    base = Path(ref).name
    if base.endswith((".yaml", ".yml")):
        base = base.rsplit(".", 1)[0]
    base = base.replace("-", " ").replace("_", " ")
    return " ".join(w.capitalize() for w in base.split()) if base else ""


def _edge_type_raw(edge: dict) -> str:
    return str(edge.get("type", "")).strip()


def collect_relationship_types(graph: dict) -> list[str]:
    """Types present in the graph: ODPG spec order (camelCase literals), then other types A–Z."""
    seen_lower_to_raw: dict[str, str] = {}
    for edge in graph.get("edges") or []:
        raw = _edge_type_raw(edge)
        if not raw:
            continue
        lo = raw.lower()
        if lo not in seen_lower_to_raw:
            seen_lower_to_raw[lo] = raw
    ordered_core: list[str] = []
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


def _build_legend_relationship_html(relationship_types: list[str], graph: dict) -> str:
    edges = graph.get("edges") or []

    def sample_edge(label_raw: str) -> dict:
        lo = label_raw.lower()
        for e in edges:
            if _edge_type_raw(e).lower() == lo:
                return e
        return {}

    blocks: list[str] = []
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
        display_name = _ref_to_display_name(node["ref"])
        vis_nodes.append(
            {
                "id": node["id"],
                "label": node["id"],
                "title": (
                    f"ID: {node['id']}\n"
                    f"Type: {node['type']}\n"
                    f"Ref: {node['ref']}"
                ),
                "group": node["type"],
                "ref": node["ref"],
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

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ODPG Graph Explorer — {html.escape(graph_title)}</title>
  <script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
  <style>
    :root {{
      --topbar-bg: #005316;
      --topbar-fg: #f8fafc;
      --topbar-muted: #fff;
      --canvas-bg: #ffffff;
      --border: #e2e8f0;
      --inspector-bg: #f8fafc;
      --accent: #2563eb;
    }}

    * {{ box-sizing: border-box; }}

    html {{
      height: 100%;
    }}

    body {{
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      background: #eef2f7;
      color: #0f172a;
      height: 100%;
      max-height: 100dvh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    html:fullscreen {{
      width: 100%;
      height: 100%;
      background: #eef2f7;
    }}

    html:fullscreen body {{
      max-height: none;
      height: 100%;
    }}

    .topbar {{
      flex-shrink: 0;
      display: grid;
      grid-template-columns: minmax(160px, 1fr) minmax(0, 2.2fr) minmax(160px, 1fr);
      align-items: center;
      gap: 12px;
      padding: 10px 20px;
      background: var(--topbar-bg);
      color: var(--topbar-fg);
      border-bottom: 1px solid #003d10;
      min-height: 52px;
    }}

    .topbar-brand {{
      font-weight: 700;
      font-size: 14px;
      letter-spacing: 0.02em;
      color: var(--topbar-fg);
    }}

    .topbar-center {{
      text-align: center;
      min-width: 0;
    }}

    .topbar-graph-title {{
      display: block;
      font-size: 17px;
      font-weight: 600;
      line-height: 1.25;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .topbar-graph-meta {{
      display: block;
      font-size: 12px;
      color: var(--topbar-muted);
      margin-top: 2px;
    }}

    .topbar-actions {{
      display: flex;
      justify-content: flex-end;
      gap: 6px;
    }}

    .icon-btn {{
      width: 36px;
      height: 36px;
      border: none;
      border-radius: 8px;
      background: transparent;
      color: var(--topbar-muted);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}

    .icon-btn:hover {{
      background: rgba(148, 163, 184, 0.15);
      color: var(--topbar-fg);
    }}

    .workspace {{
      flex: 1 1 auto;
      min-height: 0;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}

    .workspace-main {{
      flex: 1 1 auto;
      min-height: 0;
      display: grid;
      grid-template-columns: 1fr minmax(280px, 380px);
      grid-template-rows: 1fr;
      overflow: hidden;
    }}

    .canvas-col {{
      display: flex;
      flex-direction: column;
      background: var(--canvas-bg);
      min-height: 0;
      min-width: 0;
      overflow: hidden;
    }}

    .canvas-graph-area {{
      position: relative;
      flex: 1 1 auto;
      min-height: 120px;
      min-width: 0;
    }}

    #graph {{
      width: 100%;
      height: 100%;
      min-height: 0;
    }}

    .vis-tooltip,
    div.vis-network-tooltip {{
      white-space: pre-line !important;
    }}

    .minimap {{
      position: absolute;
      top: 12px;
      left: 12px;
      width: 200px;
      height: 132px;
      z-index: 5;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
      overflow: hidden;
    }}

    .graph-tools {{
      position: absolute;
      top: 50%;
      left: 12px;
      transform: translateY(-50%);
      z-index: 6;
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 6px;
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 10px;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
    }}

    .graph-tools button {{
      width: 34px;
      height: 34px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fff;
      font-size: 18px;
      line-height: 1;
      cursor: pointer;
      color: #334155;
    }}

    .graph-tools button:hover {{
      background: #f1f5f9;
    }}

    .graph-tools button.is-locked {{
      background: #e0f2fe;
      border-color: #7dd3fc;
      color: #0369a1;
    }}

    .graph-legend {{
      flex-shrink: 0;
      width: 100%;
      background: #f8fafc;
      border-top: 1px solid var(--border);
      padding: 10px 18px 12px;
      overflow-x: auto;
      overflow-y: visible;
    }}

    .graph-legend-inner {{
      display: grid;
      grid-template-columns: 1fr auto 1.15fr;
      gap: 0 20px;
      align-items: stretch;
      max-width: 100%;
    }}

    .graph-legend-divider {{
      width: 1px;
      background: #e2e8f0;
      margin: 4px 0;
    }}

    .graph-legend-title {{
      margin: 0 0 10px;
      font-size: 11px;
      font-weight: 700;
      color: #475569;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}

    .graph-legend-node-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px 14px;
    }}

    .graph-legend-edge-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px 12px;
    }}

    @media (max-width: 1100px) {{
      .graph-legend-node-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .graph-legend-edge-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}

    .legend-node-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 500;
      color: #1e293b;
      white-space: nowrap;
    }}

    .legend-node-dot {{
      width: 13px;
      height: 13px;
      border-radius: 50%;
      flex-shrink: 0;
      box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.18);
    }}

    .legend-edge-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      font-weight: 600;
      color: #334155;
      letter-spacing: 0.02em;
    }}

    .legend-edge-item svg {{
      flex-shrink: 0;
    }}

    .odpg-footer {{
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      gap: 14px;
      padding: 12px 20px 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.18);
      background: linear-gradient(180deg, #0a6b22 0%, var(--topbar-bg) 100%);
      color: #ecfdf5;
      font-size: 12px;
      line-height: 1.45;
    }}

    .odpg-footer-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .odpg-footer-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
      font-weight: 600;
      color: #f0fdf4;
      font-size: 24px;
    }}

    .odpg-footer-mark {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: rgba(0, 0, 0, 0.25);
      color: #ffffff;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.04em;
      flex-shrink: 0;
    }}

    .odpg-footer-link {{
      color: #bbf7d0;
      font-weight: 700;
      text-decoration: none;
      white-space: nowrap;
    }}

    .odpg-footer-link:hover {{
      text-decoration: underline;
      color: #ffffff;
    }}

    .odpg-footer-resources {{
      display: flex;
      flex-direction: row;
      flex-wrap: nowrap;
      align-items: center;
      gap: 8px 14px;
      min-width: 0;
      width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }}

    .odpg-footer-resources h3 {{
      margin: 0;
      flex-shrink: 0;
      font-size: 11px;
      font-weight: 700;
      color: #bbf7d0;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      white-space: nowrap;
    }}

    .odpg-footer-resources a {{
      flex-shrink: 0;
      white-space: nowrap;
      color: #ffffff;
      font-weight: 600;
      text-decoration: underline;
      text-underline-offset: 2px;
    }}

    .odpg-footer-resources a:hover {{
      color: #fef08a;
    }}

    @media (max-width: 760px) {{
      .odpg-footer-top {{
        align-items: flex-start;
        flex-direction: column;
        gap: 8px;
      }}
    }}

    .inspector {{
      border-left: 1px solid var(--border);
      background: var(--inspector-bg);
      display: flex;
      flex-direction: column;
      min-height: 0;
      min-width: 0;
    }}

    .inspector-tabs {{
      display: flex;
      border-bottom: 1px solid var(--border);
      background: #fff;
    }}

    .inspector-tabs button {{
      flex: 1;
      padding: 12px 10px;
      border: none;
      background: transparent;
      font-size: 13px;
      font-weight: 600;
      color: #64748b;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
    }}

    .inspector-tabs button.is-active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
      background: #f8fafc;
    }}

    .inspector-panel {{
      flex: 1;
      overflow-y: auto;
      padding: 16px 18px 20px;
    }}

    .inspector-panel.is-hidden {{
      display: none;
    }}

    .panel-placeholder {{
      color: #64748b;
      font-size: 14px;
      line-height: 1.5;
    }}

    .panel-head {{
      display: flex;
      gap: 12px;
      align-items: flex-start;
      margin-bottom: 18px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--border);
    }}

    .type-dot {{
      width: 40px;
      height: 40px;
      border-radius: 999px;
      flex-shrink: 0;
      border: 2px solid rgba(255, 255, 255, 0.95);
      box-shadow: 0 2px 6px rgba(15, 23, 42, 0.12);
    }}

    .panel-head h2 {{
      margin: 0;
      font-size: 15px;
      font-weight: 700;
      line-height: 1.3;
    }}

    .panel-head .sub {{
      margin: 4px 0 0;
      font-size: 12px;
      color: #64748b;
      font-weight: 500;
    }}

    .field {{
      margin-bottom: 14px;
    }}

    .field label {{
      display: block;
      font-size: 11px;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .field span, .field p {{
      display: block;
      margin-top: 5px;
      font-size: 13px;
      color: #0f172a;
      word-break: break-word;
      line-height: 1.45;
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-brand"><img src="https://opendataproducts.org/odpg-v1.0/images/logo-dps-2024-f87840fa.png" alt="ODPG Logo" width="100"></div>
    <div class="topbar-center">
      <span class="topbar-graph-title">{html.escape(graph_title)}</span>
      <span class="topbar-graph-meta">{html.escape(graph_meta)}</span>
    </div>
    <div class="topbar-actions" aria-hidden="true">
      <button type="button" class="icon-btn" title="Search (placeholder)">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
      </button>
      <button type="button" class="icon-btn" title="Fit graph">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
      </button>
      <button type="button" class="icon-btn" title="Fullscreen" id="btn-fullscreen">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
      </button>
      <button type="button" class="icon-btn" title="About">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
      </button>
    </div>
  </header>

  <div class="workspace">
    <div class="workspace-main">
    <div class="canvas-col">
      <div class="canvas-graph-area">
      <nav class="graph-tools" aria-label="Zoom and layout">
        <button type="button" id="btn-zoom-in" title="Zoom in">+</button>
        <button type="button" id="btn-zoom-out" title="Zoom out">−</button>
        <button type="button" id="btn-fit" title="Fit view">⊙</button>
        <button type="button" id="btn-physics" title="Toggle physics (layout)">◎</button>
      </nav>
      <div id="minimap" class="minimap" aria-label="Overview map"></div>
      <div id="graph"></div>
      </div>
    </div>

    <aside class="inspector">
      <div class="inspector-tabs" role="tablist">
        <button type="button" id="tab-node" class="is-active" role="tab" aria-selected="true">Node details</button>
        <button type="button" id="tab-edge" role="tab" aria-selected="false">Edge details</button>
      </div>
      <div id="panel-node" class="inspector-panel" role="tabpanel">
        <p class="panel-placeholder" id="node-placeholder">Select a node on the graph to see ID, type, reference, and description.</p>
        <div id="node-detail" style="display:none"></div>
      </div>
      <div id="panel-edge" class="inspector-panel is-hidden" role="tabpanel">
        <p class="panel-placeholder" id="edge-placeholder">Select an edge to see relationship type and confidence.</p>
        <div id="edge-detail" style="display:none"></div>
      </div>
    </aside>
    </div>

    <div class="graph-legend" role="region" aria-label="Graph legend">
        <div class="graph-legend-inner">
          <div class="graph-legend-col">
            <h3 class="graph-legend-title">Node Types</h3>
            <div class="graph-legend-node-grid">
              <div class="legend-node-item"><span class="legend-node-dot" style="background:#16a34a"></span>UseCase</div>
              <div class="legend-node-item"><span class="legend-node-dot" style="background:#0284c7"></span>DataProduct</div>
              <div class="legend-node-item"><span class="legend-node-dot" style="background:#7c3aed"></span>API</div>
              <div class="legend-node-item"><span class="legend-node-dot" style="background:#ea580c"></span>BusinessObjective</div>
              <div class="legend-node-item"><span class="legend-node-dot" style="background:#0d9488"></span>KPI</div>
              <div class="legend-node-item"><span class="legend-node-dot" style="background:#db2777"></span>Policy</div>
              <div class="legend-node-item"><span class="legend-node-dot" style="background:#0e7490"></span>Agent</div>
              <div class="legend-node-item"><span class="legend-node-dot" style="background:#fb923c"></span>StrategicOpportunity</div>
            </div>
          </div>
          <div class="graph-legend-divider" aria-hidden="true"></div>
          <div class="graph-legend-col">
            <h3 class="graph-legend-title">Relationship Types</h3>
            <div class="graph-legend-edge-grid">
{legend_edges_html}
            </div>
          </div>
        </div>
      </div>

      <footer class="odpg-footer">
        <div class="odpg-footer-top">
          <div class="odpg-footer-brand">
            <span>Open Data Product Graphs Explorer</span>
          </div>
          <a class="odpg-footer-link" href="https://opendataproducts.org/odpg-v1.0" target="_blank" rel="noopener noreferrer">
            opendataproducts.org/odpg-v1.0
          </a>
        </div>
        <nav class="odpg-footer-resources" aria-label="ODPG 1.0 specification, schemas, and contribution">
          <h3>Specification &amp; schemas</h3>
          <a href="https://github.com/Open-Data-Product-Initiative/odpg-v1.0" target="_blank" rel="noopener noreferrer" title="Official source repository for the ODPG 1.0 specification">Open Data Product Graphs 1.0 on GitHub</a>
          <a href="https://opendataproducts.org/odpg-v1.0/schema/graph.yaml" target="_blank" rel="noopener noreferrer" title="Machine-readable schema definition in YAML format">ODPG YAML Schema</a>
          <a href="https://opendataproducts.org/odpg-v1.0/schema/graph.json" target="_blank" rel="noopener noreferrer" title="Machine-readable schema definition in JSON format">ODPG JSON Schema</a>
          <a href="https://github.com/Open-Data-Product-Initiative/odpg-v1.0/issues" target="_blank" rel="noopener noreferrer" title="Submit issues or suggestions to the specification maintainers">Raise an issue in GitHub</a>
        </nav>
      </footer>
  </div>

  <script>
    (function () {{
    function escHtml(s) {{
      return String(s == null ? "" : s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
    }}

    const TYPE_COLORS = {{
      UseCase: "#16a34a",
      BusinessObjective: "#ea580c",
      StrategicOpportunity: "#f97316",
      DataProduct: "#0284c7",
      Agent: "#0e7490",
      API: "#7c3aed",
      Policy: "#db2777",
      KPI: "#0d9488"
    }};

    const RELATIONSHIP_TYPES = {json.dumps(relationship_types)};
    const ODPG_SUPPORTED_EDGE_TYPES_ORDERED = {odpg_supported_ordered_json};
    const ODPG_EDGE_TYPE_DESCRIPTIONS = {odpg_descriptions_json};

    if (typeof vis === "undefined") {{
      document.getElementById("graph").innerHTML =
        "<p style=\\"padding:24px;font-family:sans-serif;line-height:1.5\\">" +
        "The graph library did not load (network or CDN blocked). " +
        "Serve this folder over HTTP or allow scripts from cdn.jsdelivr.net, then reload." +
        "</p>";
      return;
    }}

    const nodes = new vis.DataSet({json.dumps(vis_nodes, indent=2, ensure_ascii=False)});
    const edges = new vis.DataSet({json.dumps(vis_edges, indent=2, ensure_ascii=False)});

    const container = document.getElementById("graph");
    const data = {{ nodes: nodes, edges: edges }};

    const groupCard = (border) => ({{
      color: {{
        background: "#ffffff",
        border: border,
        highlight: {{ background: "#ffffff", border: border }},
        hover: {{ background: "#ffffff", border: border }}
      }}
    }});

    const options = {{
      autoResize: true,
      nodes: {{
        shape: "box",
        margin: 16,
        borderWidth: 2,
        shadow: {{
          enabled: true,
          color: "rgba(15,23,42,0.1)",
          size: 10,
          x: 0,
          y: 3
        }},
        font: {{
          size: 13,
          face: "Segoe UI,system-ui,sans-serif",
          color: "#0f172a"
        }},
        shapeProperties: {{ borderRadius: 12 }}
      }},
      edges: {{
        width: 1.25,
        smooth: {{ type: "dynamic" }},
        color: {{ inherit: false }},
        font: {{
          size: 10,
          align: "middle",
          face: "Segoe UI,system-ui,sans-serif",
          color: "#334155",
          strokeWidth: 0,
          background: "rgba(255,255,255,0.92)"
        }}
      }},
      groups: {{
        DataProduct: groupCard("#0284c7"),
        UseCase: groupCard("#16a34a"),
        BusinessObjective: groupCard("#ea580c"),
        KPI: groupCard("#0d9488"),
        Policy: groupCard("#db2777"),
        API: groupCard("#7c3aed"),
        Agent: groupCard("#0e7490"),
        StrategicOpportunity: groupCard("#f97316")
      }},
      physics: {{
        enabled: true,
        stabilization: {{ iterations: 280, updateInterval: 25, fit: true }},
        barnesHut: {{
          gravitationalConstant: -3400,
          centralGravity: 0.11,
          springLength: 280,
          springConstant: 0.032,
          damping: 0.58,
          avoidOverlap: 0.42
        }}
      }},
      interaction: {{
        hover: true,
        dragNodes: true,
        dragView: true,
        zoomView: true,
        multiselect: false,
        navigationButtons: false,
        keyboard: true
      }}
    }};

    const network = new vis.Network(container, data, options);
    let minimapNetwork = null;
    let physicsUserOn = false;

    document.addEventListener("fullscreenchange", function () {{
      window.requestAnimationFrame(function () {{
        network.redraw();
        if (minimapNetwork) minimapNetwork.redraw();
      }});
    }});

    function persistAllNodePositions() {{
      network.stopSimulation();
      const ids = nodes.getIds();
      if (!ids.length) return;
      const pos = network.getPositions(ids);
      const upd = ids.map(function (id) {{
        const pt = pos[id];
        if (!pt) return null;
        return {{ id: id, x: pt.x, y: pt.y, fixed: false }};
      }}).filter(Boolean);
      if (upd.length) nodes.update(upd);
    }}

    function persistNodePositions(ids) {{
      if (!ids || !ids.length) return;
      const pos = network.getPositions(ids);
      const upd = ids.map(function (id) {{
        const pt = pos[id];
        if (!pt) return null;
        return {{ id: id, x: pt.x, y: pt.y, fixed: false }};
      }}).filter(Boolean);
      if (upd.length) nodes.update(upd);
    }}

    function disablePhysicsAfterLayout() {{
      network.stopSimulation();
      network.setOptions({{ physics: {{ enabled: false }} }});
      physicsUserOn = false;
      document.getElementById("btn-physics").classList.add("is-locked");
      persistAllNodePositions();
      if (!minimapNetwork) {{
        minimapNetwork = new vis.Network(document.getElementById("minimap"), data, {{
          autoResize: false,
          width: "200px",
          height: "132px",
          nodes: options.nodes,
          edges: Object.assign({{}}, options.edges, {{ smooth: {{ type: "continuous" }} }}),
          groups: options.groups,
          physics: false,
          interaction: {{ zoomView: true, dragView: true, dragNodes: false, selectable: true }}
        }});
        minimapNetwork.fit({{ animation: false }});
      }} else {{
        minimapNetwork.fit({{ animation: false }});
      }}
    }}

    let layoutDone = false;
    function onLayoutStable() {{
      if (layoutDone) return;
      layoutDone = true;
      disablePhysicsAfterLayout();
    }}
    network.once("stabilizationIterationsDone", onLayoutStable);
    network.once("stabilized", function () {{
      setTimeout(function () {{
        if (!layoutDone) onLayoutStable();
      }}, 300);
    }});

    network.on("dragStart", function () {{
      if (!physicsUserOn) network.stopSimulation();
    }});

    network.on("dragEnd", function (p) {{
      if (!p.nodes || !p.nodes.length) return;
      network.stopSimulation();
      window.setTimeout(function () {{
        if (physicsUserOn) {{
          persistNodePositions(p.nodes);
        }} else {{
          persistAllNodePositions();
        }}
      }}, 0);
    }});

    document.getElementById("btn-zoom-in").addEventListener("click", function () {{
      const s = network.getScale();
      network.moveTo({{ scale: s * 1.25, animation: true }});
    }});
    document.getElementById("btn-zoom-out").addEventListener("click", function () {{
      const s = network.getScale();
      network.moveTo({{ scale: s * 0.8, animation: true }});
    }});
    document.getElementById("btn-fit").addEventListener("click", function () {{
      network.fit({{ animation: true }});
      if (minimapNetwork) minimapNetwork.fit({{ animation: false }});
    }});
    document.querySelector(".topbar-actions .icon-btn:nth-child(2)").addEventListener("click", function () {{
      network.fit({{ animation: true }});
    }});

    document.getElementById("btn-physics").addEventListener("click", function () {{
      const btn = document.getElementById("btn-physics");
      physicsUserOn = !physicsUserOn;
      network.setOptions({{ physics: {{ enabled: physicsUserOn }} }});
      if (physicsUserOn) {{
        nodes.update(nodes.get().map(function (n) {{
          return {{ id: n.id, fixed: false }};
        }}));
        btn.classList.remove("is-locked");
      }} else {{
        network.stopSimulation();
        network.setOptions({{ physics: {{ enabled: false }} }});
        btn.classList.add("is-locked");
        persistAllNodePositions();
      }}
    }});

    document.getElementById("btn-fullscreen").addEventListener("click", function () {{
      const el = document.documentElement;
      if (!document.fullscreenElement) {{
        if (el.requestFullscreen) el.requestFullscreen();
      }} else if (document.exitFullscreen) {{
        document.exitFullscreen();
      }}
    }});

    const tabNode = document.getElementById("tab-node");
    const tabEdge = document.getElementById("tab-edge");
    const panelNode = document.getElementById("panel-node");
    const panelEdge = document.getElementById("panel-edge");

    tabNode.addEventListener("click", function () {{
      tabNode.classList.add("is-active");
      tabEdge.classList.remove("is-active");
      tabNode.setAttribute("aria-selected", "true");
      tabEdge.setAttribute("aria-selected", "false");
      panelNode.classList.remove("is-hidden");
      panelEdge.classList.add("is-hidden");
    }});
    tabEdge.addEventListener("click", function () {{
      tabEdge.classList.add("is-active");
      tabNode.classList.remove("is-active");
      tabEdge.setAttribute("aria-selected", "true");
      tabNode.setAttribute("aria-selected", "false");
      panelEdge.classList.remove("is-hidden");
      panelNode.classList.add("is-hidden");
    }});

    function showNodePanel(node) {{
      document.getElementById("node-placeholder").style.display = "none";
      const wrap = document.getElementById("node-detail");
      wrap.style.display = "block";
      const dot = TYPE_COLORS[node.type] || "#64748b";
      const desc = escHtml(node.displayName || node.type);
      wrap.innerHTML =
        '<div class="panel-head">' +
          '<span class="type-dot" style="background:' + dot + '"></span>' +
          "<div><h2>" + escHtml(node.id) + '</h2><p class="sub">' + desc + "</p></div>" +
        "</div>" +
        '<div class="field"><label>ID</label><span>' + escHtml(node.id) + "</span></div>" +
        '<div class="field"><label>Type</label><span>' + escHtml(node.type) + "</span></div>" +
        '<div class="field"><label>Reference</label><span>' + escHtml(node.ref) + "</span></div>" +
        '<div class="field"><label>Description</label><p>' + desc + "</p></div>";
      tabNode.click();
    }}

    function showEdgePanel(edge) {{
      document.getElementById("edge-placeholder").style.display = "none";
      const wrap = document.getElementById("edge-detail");
      wrap.style.display = "block";
      const lines = String(edge.label || "").split("\\n");
      const rawTypeKey = (lines[0] || "").trim();
      const typeLine = escHtml(rawTypeKey);
      const confLine = escHtml(lines[1] || "(" + edge.confidence + ")");
      const odpgDesc = ODPG_EDGE_TYPE_DESCRIPTIONS[(rawTypeKey || "").toLowerCase()] || "";
      const descHtml = odpgDesc
        ? '<div class="field"><label>ODPG definition</label><p>' + escHtml(odpgDesc) + "</p></div>"
        : "";
      wrap.innerHTML =
        '<div class="panel-head"><div><h2>Relationship</h2><p class="sub">' + typeLine + " " + confLine + "</p></div></div>" +
        '<div class="field"><label>From</label><span>' + escHtml(edge.from) + "</span></div>" +
        '<div class="field"><label>To</label><span>' + escHtml(edge.to) + "</span></div>" +
        '<div class="field"><label>Type</label><span>' + typeLine + "</span></div>" +
        '<div class="field"><label>Confidence</label><span>' + escHtml(edge.confidence) + "</span></div>" +
        descHtml;
      tabEdge.click();
    }}

    network.on("selectNode", function (params) {{
      if (!params.nodes.length) return;
      const node = nodes.get(params.nodes[0]);
      showNodePanel(node);
    }});

    network.on("selectEdge", function (params) {{
      if (!params.edges.length) return;
      const edge = edges.get(params.edges[0]);
      showEdgePanel(edge);
    }});

    network.on("deselectNode", function () {{
      if (network.getSelectedNodes().length === 0 && network.getSelectedEdges().length === 0) {{
        document.getElementById("node-placeholder").style.display = "";
        document.getElementById("node-detail").style.display = "none";
      }}
    }});

    network.on("deselectEdge", function () {{
      if (network.getSelectedEdges().length === 0 && network.getSelectedNodes().length === 0) {{
        document.getElementById("edge-placeholder").style.display = "";
        document.getElementById("edge-detail").style.display = "none";
      }}
    }});
    }})();
  </script>
</body>
</html>
"""


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
