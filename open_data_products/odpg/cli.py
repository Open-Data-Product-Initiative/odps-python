"""Command line entry points for ODPG SDK helpers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

import yaml

from .graph import (
    generate_graph_explorer,
    load_graph,
    render_graph_object_records,
    search_graph_objects,
    validate_graph,
)


def search_main(argv: Optional[List[str]] = None) -> int:
    """Search ODPG graph object records from the command line."""
    parser = argparse.ArgumentParser(
        description="Search ODPG graph object records.",
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Keyword query, for example: governance traversal",
    )
    parser.add_argument(
        "--id",
        dest="object_id",
        help="Return one object by id, for example: DataProduct",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON array output")
    args = parser.parse_args(argv)

    records = search_graph_objects(args.query, object_id=args.object_id)
    if args.json:
        print(json.dumps(records, indent=2))
    else:
        sys.stdout.write(render_graph_object_records(records))
    return 0 if records else 1


def validate_main(argv: Optional[List[str]] = None) -> int:
    """Validate an ODPG graph from the command line."""
    parser = argparse.ArgumentParser(description="Validate an ODPG graph YAML file.")
    parser.add_argument(
        "graph",
        nargs="?",
        help="Path to an ODPG YAML graph file. Defaults to bundled graph.",
    )
    args = parser.parse_args(argv)

    try:
        graph = load_graph(args.graph) if args.graph else load_graph()
    except FileNotFoundError as exc:
        print(f"File not found: {exc.filename}", file=sys.stderr)
        return 1
    except (yaml.YAMLError, ValueError) as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    result = validate_graph(graph)
    if not result.valid:
        path = args.graph or "(bundled ODPG graph)"
        print(f"{path}: invalid ODPG graph", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"{args.graph or '(bundled ODPG graph)'}: valid ODPG graph")
    return 0


def generate_main(argv: Optional[List[str]] = None) -> int:
    """Generate an ODPG graph explorer from the command line."""
    parser = argparse.ArgumentParser(
        description="Generate graph-explorer.html from an ODPG graph YAML file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="graph_yaml",
        type=Path,
        help="Path to graph YAML file. Defaults to bundled graph.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("graph-explorer.html"),
        metavar="PATH",
        help="Output HTML file path",
    )
    args = parser.parse_args(argv)

    try:
        output = generate_graph_explorer(args.graph_yaml, args.output)
    except (FileNotFoundError, yaml.YAMLError, ValueError) as exc:
        print(f"Could not generate graph explorer: {exc}", file=sys.stderr)
        return 1

    print(f"Graph Explorer generated successfully: {output}")
    return 0
