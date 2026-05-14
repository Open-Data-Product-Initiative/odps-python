"""Command line entry points for ODPC SDK helpers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

import yaml

from .catalog import (
    explain_catalog,
    load_catalog,
    load_schema,
    render_object_records,
    search_objects,
    validate_catalog,
)


def search_main(argv: Optional[List[str]] = None) -> int:
    """Search ODPC object records from the command line."""
    parser = argparse.ArgumentParser(
        description="Search ODPC agent-friendly object records.",
    )
    parser.add_argument("query", nargs="?", help="Keyword query, for example: demand")
    parser.add_argument(
        "--id",
        dest="object_id",
        help="Return one object by id, for example: ProductReference",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON array output")
    args = parser.parse_args(argv)

    records = search_objects(args.query, object_id=args.object_id)
    if args.json:
        print(json.dumps(records, indent=2))
    else:
        sys.stdout.write(render_object_records(records))
    return 0 if records else 1


def explain_main(argv: Optional[List[str]] = None) -> int:
    """Explain an ODPC catalog from the command line."""
    parser = argparse.ArgumentParser(
        description="Explain an ODPC catalog file for humans and AI agents."
    )
    parser.add_argument("catalog", help="Path to an ODPC YAML or JSON catalog file")
    parser.add_argument("--json", action="store_true", help="Emit JSON object output")
    args = parser.parse_args(argv)

    path = Path(args.catalog)
    try:
        document = load_catalog(path)
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, yaml.YAMLError, ValueError) as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    summary = explain_catalog(document, path=path)
    if args.json:
        print(
            json.dumps(
                {
                    "spec": "odpc",
                    "kind": "Catalog",
                    "path": str(path),
                    "summary": summary,
                },
                indent=2,
            )
        )
    else:
        print(summary, end="")
    return 0


def validate_main(argv: Optional[List[str]] = None) -> int:
    """Validate an ODPC catalog from the command line."""
    parser = argparse.ArgumentParser(
        description="Validate an ODPC catalog file against the ODPC schema."
    )
    parser.add_argument("catalog", help="Path to an ODPC YAML or JSON catalog file")
    parser.add_argument(
        "--schema", help="Schema path. Defaults to bundled ODPC schema."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON object output")
    args = parser.parse_args(argv)

    try:
        catalog = load_catalog(args.catalog)
        schema = load_schema(args.schema) if args.schema else None
        result = validate_catalog(catalog, schema=schema)
    except FileNotFoundError as exc:
        print(f"File not found: {exc.filename}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, yaml.YAMLError, ValueError) as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not result.valid:
        if args.json:
            print(
                json.dumps(
                    {
                        "valid": False,
                        "spec": "odpc",
                        "kind": "Catalog",
                        "path": args.catalog,
                        "errors": result.errors,
                    },
                    indent=2,
                )
            )
            return 1
        print(f"{args.catalog}: invalid ODPC catalog", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "valid": True,
                    "spec": "odpc",
                    "kind": "Catalog",
                    "path": args.catalog,
                    "errors": [],
                },
                indent=2,
            )
        )
    else:
        print(f"{args.catalog}: valid ODPC catalog")
    return 0
