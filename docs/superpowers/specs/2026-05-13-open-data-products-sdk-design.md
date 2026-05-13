# Open Data Products Python SDK Design

Date: 2026-05-13

## Purpose

The current Python library is named and structured around ODPS, the Open Data Product Specification. The OpenDataProducts.org standards family is expanding to include related specifications such as ODPV, ODPC, and ODPG. The Python library should become a comprehensive SDK for the standards family instead of remaining an ODPS-only package with unrelated scripts attached.

The long-term package name should be `open-data-products`, with the Python namespace `open_data_products`.

## Goals

- Support the full OpenDataProducts.org standards family in one coherent Python SDK.
- Preserve backward compatibility for existing users of `odps-python` and `import odps`.
- Turn existing spec repository scripts into importable library modules with CLI wrappers.
- Share common IO, schema, validation, multilingual, and error-handling behavior across specifications.
- Allow ODPS, ODPV, ODPC, and ODPG to evolve independently inside clear module boundaries.

## Non-Goals

- Do not redesign the ODPS v4.1 data model during the first migration.
- Do not immediately implement complete ODPC and ODPG support before the package structure is stable.
- Do not copy scripts into the package as opaque standalone files when they can be expressed as reusable APIs.
- Do not break existing ODPS users in the first release of the broader SDK.

## Package Identity

The public package should move toward:

```bash
pip install open-data-products
```

The primary Python namespace should be:

```python
import open_data_products
```

Spec-specific imports should use clear subpackages:

```python
from open_data_products.odps import OpenDataProduct
from open_data_products.odpv import Vocabulary
from open_data_products.odpc import Catalog
from open_data_products.odpg import Graph
```

The existing `odps` package should remain as a compatibility wrapper for at least one major release:

```python
from odps import OpenDataProduct
```

That wrapper should re-export the ODPS implementation from `open_data_products.odps`.

## Target Package Structure

```text
open_data_products/
  __init__.py
  shared/
    __init__.py
    io.py
    errors.py
    validation.py
    schema.py
    multilingual.py
  odps/
    __init__.py
    core.py
    models.py
    validation.py
    validators.py
    enums.py
    protocols.py
  odpv/
    __init__.py
    vocabulary.py
    search.py
    artifacts.py
    validation.py
    data/
      odpv.yaml
      odpv.json
      terms.jsonl
  odpc/
    __init__.py
    catalog.py
    models.py
    search.py
    validation.py
    data/
  odpg/
    __init__.py
    graph.py
    models.py
    validation.py
    export.py
    data/
  cli.py
odps/
  __init__.py
```

The `odps` directory should only contain compatibility exports after migration. New implementation code should live under `open_data_products`.

## Module Responsibilities

### `open_data_products.shared`

Shared utilities used by multiple specifications:

- JSON and YAML load/dump helpers.
- File loading and saving.
- Common exception hierarchy.
- Schema validation helpers.
- Multilingual field helpers.
- Common validation result types.

### `open_data_products.odps`

The existing ODPS v4.1 implementation:

- `OpenDataProduct`.
- ODPS models.
- ODPS validators.
- ODPS enums and protocols.
- Existing JSON/YAML serialization behavior.

The first migration should move code with minimal behavior changes.

### `open_data_products.odpv`

ODPV vocabulary support based on the current `odpv-v1.0/scripts` toolkit:

- Load canonical vocabulary data.
- Validate vocabulary structure and required term fields.
- Generate derived vocabulary artifacts.
- Search vocabulary terms.
- Provide packaged vocabulary data for normal library use.

The current ODPV scripts should become importable modules first, then CLI commands.

### `open_data_products.odpc`

ODPC catalog support:

- Catalog models.
- Catalog schema validation.
- Catalog object search and explanation helpers.
- Packaged schema and sample catalog artifacts where appropriate.

ODPC should be added after ODPS migration and ODPV tooling are stable.

### `open_data_products.odpg`

ODPG graph support:

- Graph, node, and edge models.
- Graph validation.
- Import/export helpers for graph-oriented formats.
- Packaged schema and graph artifacts where appropriate.

ODPG should be added after ODPC because it depends conceptually on shared catalog and vocabulary terms.

## CLI Design

The SDK should expose one command namespace:

```bash
odp validate product.yaml
odp odpv search "customer churn"
odp odpv generate --check
odp odpc validate catalog.yaml
odp odpg validate graph.yaml
```

The CLI should call the same library APIs used by Python consumers. It should not duplicate business logic.

## Migration Plan

1. Create `open_data_products` package and move the current ODPS implementation into `open_data_products.odps`.
2. Replace the current top-level `odps` package with compatibility re-exports.
3. Update packaging metadata to include both `open_data_products` and the compatibility `odps` namespace.
4. Rename project metadata toward `open-data-products`.
5. Add tests proving existing imports still work:

   ```python
   from odps import OpenDataProduct
   from open_data_products.odps import OpenDataProduct
   ```

6. Port ODPV scripts into importable modules:
   - `vocabulary.py`
   - `validation.py`
   - `artifacts.py`
   - `search.py`

7. Package ODPV vocabulary artifacts as library data.
8. Add the `odp` CLI entry point.
9. Add ODPC support.
10. Add ODPG support.

## Testing Strategy

- Preserve existing ODPS tests and run them against the compatibility namespace.
- Add equivalent tests for `open_data_products.odps`.
- Add ODPV unit tests for validation, artifact generation, and search without subprocess-only coverage.
- Add CLI smoke tests for the `odp` command after CLI entry points exist.
- Add fixture-based tests for packaged schema and vocabulary data.
- Add migration tests that confirm old imports and new imports refer to compatible classes.

## Release Strategy

The first release should prioritize compatibility:

- Publish as `open-data-products` when PyPI ownership and release process are ready.
- Keep `odps-python` as a transition package or previous package line if practical.
- Keep `import odps` working.
- Document the new namespace as preferred.
- Mark direct `odps` imports as compatible but legacy once the new package is established.

## Open Questions

- Whether `odps-python` should become a thin dependency package that installs `open-data-products`, or whether it should remain as the historical ODPS-only package line.
- Whether the CLI command should be `odp`, `odps`, or `open-data-products`. The current design chooses `odp` because it is short and applies to the whole standards family.
- How much generated source data from ODPC and ODPG should be packaged versus loaded from user-provided files.
