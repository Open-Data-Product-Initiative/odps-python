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
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 1
