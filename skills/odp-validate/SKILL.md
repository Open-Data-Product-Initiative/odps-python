---
name: odp-validate
description: Validate any Open Data Products document (ODPS, ODPC, ODPG, ODPV) — auto-detects spec, runs the matching schema + business-rule checks, and returns a structured pass/fail with errors and warnings.
allowed-tools:
  - Bash
  - Read
paths:
  - "**/*.odps.yaml"
  - "**/*.odps.json"
  - "**/*.odpc.yaml"
  - "**/*.odpc.json"
  - "**/*.odpg.yaml"
  - "**/*.odpg.json"
  - "**/*.odpv.yaml"
  - "**/*.odpv.json"
---

# Open Data Products: Validate

Activate when the user asks to validate, lint, or check an Open Data Products
document, or when an ODP file appears in the diff.

## How

Prefer the CLI; fall back to the Python API when scripting.

```bash
# JSON output for parsing
open-data-products validate path/to/product.yaml --json

# Human output
open-data-products validate path/to/product.yaml
```

Programmatic:

```python
from open_data_products import validate_document
result = validate_document("path/to/product.yaml")
result.valid, result.spec, result.kind, result.errors, result.warnings
```

## When detection is ambiguous

Heuristics use the document's `schema` URL, `kind` field, and structural
shape. If detection misfires, the file likely lacks a `schema:` declaration
— add the canonical URL from opendataproducts.org.

## Reporting

Lead with `valid`, then list errors before warnings. Quote each error
verbatim from the result so the user can grep for the field name.
