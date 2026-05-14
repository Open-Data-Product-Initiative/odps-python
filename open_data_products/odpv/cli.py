"""Command line entry points for ODPV SDK helpers."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .vocabulary import (
    build_artifacts,
    render_search_results,
    search_vocabulary,
    validate_vocabulary,
    write_artifacts,
)


def search_main(argv: Optional[List[str]] = None) -> int:
    """Search ODPV vocabulary terms from the command line."""
    parser = argparse.ArgumentParser(description="Search ODPV vocabulary terms.")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--limit", type=int, default=5, help="Maximum number of matches"
    )
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON"
    )
    args = parser.parse_args(argv)

    results = search_vocabulary(args.query, limit=args.limit)
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=True))
    else:
        sys.stdout.write(render_search_results(results))
    return 0


def validate_main(argv: Optional[List[str]] = None) -> int:
    """Validate bundled ODPV vocabulary data from the command line."""
    parser = argparse.ArgumentParser(
        description="Validate bundled ODPV vocabulary data."
    )
    parser.parse_args(argv)

    result = validate_vocabulary()
    if not result.valid:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "Validation OK "
        f"terms={result.term_count} "
        f"relationships={result.relationship_count} "
        f"sections={result.section_count}"
    )
    return 0


def generate_main(argv: Optional[List[str]] = None) -> int:
    """Generate derived ODPV vocabulary artifacts from bundled data."""
    parser = argparse.ArgumentParser(
        description="Generate derived ODPV vocabulary artifacts."
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=".",
        help="Directory for generated artifacts. Defaults to the current directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated artifacts under output_dir are not in sync.",
    )
    args = parser.parse_args(argv)

    result = validate_vocabulary()
    if not result.valid:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    changed = write_artifacts(args.output_dir, check=args.check)
    if args.check and changed:
        for path in changed:
            print(f"Out of sync: {path}")
        return 1

    if args.check:
        print("Vocabulary artifacts are in sync")
    else:
        print(f"Generated {len(build_artifacts())} vocabulary artifacts")
    return 0
