from pathlib import Path

from open_data_products.odpg import (
    build_graph_explorer_html,
    collect_relationship_types,
    generate_graph_explorer,
    load_graph,
    search_graph_objects,
    validate_graph,
)
from open_data_products.odpg.cli import generate_main, search_main, validate_main


def test_bundled_graph_loads_and_validates():
    graph = load_graph()

    result = validate_graph(graph)

    assert result.valid
    assert result.errors == []
    assert graph["kind"] == "DataProductGraph"
    assert len(graph["nodes"]) == 9
    assert len(graph["edges"]) == 13


def test_relationship_types_keep_odpg_order():
    graph = load_graph()

    relationship_types = collect_relationship_types(graph)

    assert relationship_types[:4] == ["uses", "supports", "contributesTo", "measures"]
    assert "governedBy" in relationship_types


def test_search_graph_objects_by_id_and_keywords():
    exact = search_graph_objects(object_id="DataProduct")
    keyword = search_graph_objects("strategic graph opportunity")

    assert exact[0]["id"] == "DataProduct"
    assert keyword[0]["id"] == "StrategicOpportunity"


def test_generate_graph_explorer_writes_html(tmp_path):
    output = tmp_path / "graph-explorer.html"

    generate_graph_explorer(output_file=output)

    html = output.read_text(encoding="utf-8")
    assert "ODPG Graph Explorer" in html
    assert "Aviation Data Product Value Graph" in html
    assert "vis-network" in html


def test_build_graph_explorer_html_returns_document():
    html = build_graph_explorer_html(load_graph())

    assert html.startswith("\n<!DOCTYPE html>")
    assert "GRAPH-AVIATION-001" in html


def test_cli_entry_points(tmp_path):
    output = tmp_path / "graph-explorer.html"

    assert validate_main([]) == 0
    assert search_main(["--id", "DataProduct", "--json"]) == 0
    assert generate_main(["--output", str(output)]) == 0
    assert output.exists()


def test_invalid_graph_reports_missing_reference():
    graph = load_graph()
    graph["edges"] = [
        {
            "from": "missing",
            "to": "DP-AVIATION-001",
            "type": "uses",
            "confidence": "high",
        }
    ]

    result = validate_graph(graph)

    assert not result.valid
    assert any("source does not match any node id" in error for error in result.errors)
