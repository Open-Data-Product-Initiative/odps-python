"""Top-level command line interface for agent-oriented SDK workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .agent import (
    explain_document,
    load_document,
    resolve_references,
    validate_document,
)
from .resources import get_resource, list_resources
from .summary import load_summary


def main(argv: Optional[List[str]] = None) -> int:
    """Run the top-level Open Data Products CLI."""
    parser = argparse.ArgumentParser(
        prog="open-data-products",
        description="Agent-oriented tools for the Open Data Products SDK.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a document")
    validate_parser.add_argument("document", help="Path to an ODPS, ODPC, or ODPG file")
    validate_parser.add_argument("--json", action="store_true", help="Emit JSON")

    explain_parser = subparsers.add_parser("explain", help="Explain a document")
    explain_parser.add_argument("document", help="Path to an ODPS, ODPC, or ODPG file")
    explain_parser.add_argument("--json", action="store_true", help="Emit JSON")

    refs_parser = subparsers.add_parser("refs", help="List document references")
    refs_parser.add_argument("document", help="Path to an ODPS, ODPC, or ODPG file")
    refs_parser.add_argument("--json", action="store_true", help="Emit JSON")

    resources_parser = subparsers.add_parser("resources", help="List SDK resources")
    resources_parser.add_argument("--json", action="store_true", help="Emit JSON")
    resources_parser.add_argument("--id", help="Return one resource by id")

    summary_parser = subparsers.add_parser(
        "summary", help="Lightweight artifact reference for a document"
    )
    summary_parser.add_argument("document", help="Path to an ODP document")

    odpg_summary_parser = subparsers.add_parser(
        "odpg-summary", help="Summarize an ODPG graph"
    )
    odpg_summary_parser.add_argument("graph", help="Path to an ODPG graph file")

    odpg_traverse_parser = subparsers.add_parser(
        "odpg-traverse", help="Discover ODPG relationship paths from a node"
    )
    odpg_traverse_parser.add_argument("graph", help="Path to an ODPG graph file")
    odpg_traverse_parser.add_argument("--start", required=True, help="Starting node id")
    odpg_traverse_parser.add_argument(
        "--depth", type=int, default=2, help="Maximum traversal depth"
    )
    odpg_traverse_parser.add_argument(
        "--relationship", help="Optional relationship type filter"
    )
    odpg_traverse_parser.add_argument(
        "--reverse", action="store_true", help="Traverse incoming relationships"
    )

    odpg_analyze_parser = subparsers.add_parser(
        "odpg-analyze", help="Run ODPG strategic and governance checks"
    )
    odpg_analyze_parser.add_argument("graph", help="Path to an ODPG graph file")

    odpg_context_parser = subparsers.add_parser(
        "odpg-agent-context", help="Extract ODPG context around a focus node"
    )
    odpg_context_parser.add_argument("graph", help="Path to an ODPG graph file")
    odpg_context_parser.add_argument("--node", required=True, help="Focus node id")
    odpg_context_parser.add_argument(
        "--depth", type=int, default=2, help="Context traversal depth"
    )

    subparsers.add_parser("manifest", help="Emit the ARWS agent manifest").add_argument(
        "--json", action="store_true", help="Emit JSON"
    )

    subparsers.add_parser("serve", help="Run the MCP server over stdio")

    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            result = validate_document(args.document)
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            elif result.valid:
                print(f"{args.document}: valid {result.spec} {result.kind}")
            else:
                print(f"{args.document}: invalid {result.spec} {result.kind}")
                for error in result.errors:
                    print(f"- {error}")
            return 0 if result.valid else 1

        if args.command == "explain":
            document = load_document(args.document)
            summary = explain_document(document, path=Path(args.document))
            if args.json:
                result = validate_document(document, path=args.document)
                print(
                    json.dumps(
                        {
                            "spec": result.spec,
                            "kind": result.kind,
                            "path": args.document,
                            "summary": summary,
                        },
                        indent=2,
                    )
                )
            else:
                print(summary, end="")
            return 0

        if args.command == "refs":
            refs = resolve_references(args.document)
            if args.json:
                print(json.dumps([ref.to_dict() for ref in refs], indent=2))
            else:
                for ref in refs:
                    print(f"{ref.pointer} -> {ref.ref}")
            return 0

        if args.command == "resources":
            resources = [get_resource(args.id)] if args.id else list_resources()
            if args.json:
                print(
                    json.dumps([resource.to_dict() for resource in resources], indent=2)
                )
            else:
                for resource in resources:
                    print(
                        f"{resource.id}\t{resource.spec}\t{resource.type}\t{resource.path}"
                    )
            return 0

        if args.command == "summary":
            print(json.dumps(load_summary(args.document), indent=2))
            return 0

        if args.command == "odpg-summary":
            from .odpg import load_graph, summarize_graph

            print(json.dumps(summarize_graph(load_graph(args.graph)), indent=2))
            return 0

        if args.command == "odpg-traverse":
            from .odpg import load_graph, traverse_graph, validate_graph

            graph = load_graph(args.graph)
            result = validate_graph(graph)
            if not result.valid:
                print(json.dumps(result.to_dict(), indent=2))
                return 1
            paths = traverse_graph(
                graph,
                args.start,
                args.depth,
                relationship=args.relationship,
                reverse=args.reverse,
            )
            print(json.dumps({"start": args.start, "paths": paths}, indent=2))
            return 0

        if args.command == "odpg-analyze":
            from .odpg import analyze_graph, load_graph, validate_graph

            graph = load_graph(args.graph)
            result = validate_graph(graph)
            if not result.valid:
                print(json.dumps(result.to_dict(), indent=2))
                return 1
            print(
                json.dumps(
                    {"warnings": result.warnings, "analysis": analyze_graph(graph)},
                    indent=2,
                )
            )
            return 0

        if args.command == "odpg-agent-context":
            from .odpg import agent_context, load_graph, validate_graph

            graph = load_graph(args.graph)
            result = validate_graph(graph)
            if not result.valid:
                print(json.dumps(result.to_dict(), indent=2))
                return 1
            payload = agent_context(graph, args.node, args.depth)
            payload["warnings"] = result.warnings
            print(json.dumps(payload, indent=2))
            return 0

        if args.command == "manifest":
            from .mcp.manifest import generate_agent_manifest

            print(json.dumps(generate_agent_manifest(), indent=2))
            return 0

        if args.command == "serve":
            from .mcp.server import serve

            return serve()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
