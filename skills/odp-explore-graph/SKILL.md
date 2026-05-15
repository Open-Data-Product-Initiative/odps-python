---
name: odp-explore-graph
description: Browse, search, and explain Open Data Product Graphs (ODPG). Lists nodes/edges/relationship types, resolves cross-spec $refs, and can render a standalone HTML explorer.
allowed-tools:
  - Bash
  - Read
paths:
  - "**/*.odpg.yaml"
  - "**/*.odpg.json"
  - "**/graph.yaml"
---

# Open Data Products: Explore Graph

Activate when the user asks to inspect an ODPG graph, find relationships
between products, or understand how nodes connect.

## Quick read

```bash
# Compact summary: id, node count, edge count, relationship types
open-data-products explain path/to/graph.yaml
```

## Cross-spec traversal

`$ref` and `ref` values often point to ODPS products or ODPV terms. List
them all with:

```bash
open-data-products refs path/to/graph.yaml --json
```

Each entry carries `pointer` (JSON Pointer into the graph), `ref` (the
target string), `ref_type` (node / edge / schema / reference), and
`target_spec` (best-effort guess: odps / odpc / odpg / odpv).

## Standalone HTML explorer

For a visual walkthrough:

```bash
open-data-products-odpg-generate path/to/graph.yaml --output graph.html
```

Open the resulting HTML in a browser; no server required.

## When the graph is large

Use `load_summary` first to confirm size and hash before parsing the body:

```bash
open-data-products summary path/to/graph.yaml
```

That returns `{path, byte_size, line_count, sha256, spec, kind, id}`
without loading the document into the agent's context window.
