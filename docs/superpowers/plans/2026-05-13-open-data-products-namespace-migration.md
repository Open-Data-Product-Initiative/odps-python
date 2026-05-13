# Open Data Products Namespace Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the new `open_data_products` Python namespace for the existing ODPS implementation while preserving backward-compatible `odps` imports.

**Architecture:** This is the first migration slice from ODPS-only package to standards-family SDK. The existing implementation moves to `open_data_products.odps`; the top-level `odps` package becomes thin compatibility wrappers for old imports such as `from odps import OpenDataProduct` and `from odps.models import ProductDetails`.

**Tech Stack:** Python 3.8+, setuptools, pytest, PyYAML, pycountry, phonenumbers.

---

## Scope

This plan implements only the package namespace migration. It does not port ODPV scripts, add ODPC or ODPG support, add the `odp` CLI, or change ODPS v4.1 behavior. Those are separate follow-up plans after this migration is passing.

## File Structure

- Create: `open_data_products/__init__.py`
  - Public SDK root namespace.
  - Exposes package metadata and convenience ODPS exports.

- Move: `odps/core.py` to `open_data_products/odps/core.py`
  - Existing `OpenDataProduct` implementation.

- Move: `odps/models.py` to `open_data_products/odps/models.py`
  - Existing ODPS dataclasses.

- Move: `odps/validation.py` to `open_data_products/odps/validation.py`
  - Existing validation framework.

- Move: `odps/validators.py` to `open_data_products/odps/validators.py`
  - Existing standards validators.

- Move: `odps/enums.py` to `open_data_products/odps/enums.py`
  - Existing ODPS enum constants.

- Move: `odps/exceptions.py` to `open_data_products/odps/exceptions.py`
  - Existing ODPS exception hierarchy.

- Move: `odps/protocols.py` to `open_data_products/odps/protocols.py`
  - Existing protocol helpers.

- Move: `odps/__init__.py` to `open_data_products/odps/__init__.py`
  - Existing ODPS public exports.

- Create: `odps/__init__.py`
  - Compatibility exports from `open_data_products.odps`.

- Create: `odps/core.py`
  - Compatibility exports from `open_data_products.odps.core`.

- Create: `odps/models.py`
  - Compatibility exports from `open_data_products.odps.models`.

- Create: `odps/validation.py`
  - Compatibility exports from `open_data_products.odps.validation`.

- Create: `odps/validators.py`
  - Compatibility exports from `open_data_products.odps.validators`.

- Create: `odps/enums.py`
  - Compatibility exports from `open_data_products.odps.enums`.

- Create: `odps/exceptions.py`
  - Compatibility exports from `open_data_products.odps.exceptions`.

- Create: `odps/protocols.py`
  - Compatibility exports from `open_data_products.odps.protocols`.

- Modify: `pyproject.toml`
  - Rename project metadata to `open-data-products`.
  - Include `open_data_products`, `open_data_products.odps`, and `odps` packages.
  - Update coverage source to include the new namespace.

- Create: `tests/test_namespace_compatibility.py`
  - Tests new imports and old compatibility imports.

- Modify: existing tests only if import assumptions fail after the wrapper is added.
  - Keep test behavior unchanged.

---

### Task 1: Add Failing Namespace Compatibility Tests

**Files:**
- Create: `tests/test_namespace_compatibility.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_namespace_compatibility.py` with this content:

```python
"""Tests for open_data_products namespace and odps compatibility imports."""

import importlib


def test_new_namespace_exports_existing_odps_api():
    from open_data_products.odps import OpenDataProduct as NewOpenDataProduct
    from open_data_products.odps.models import ProductDetails as NewProductDetails

    details = NewProductDetails(
        name="Namespace Test",
        product_id="namespace-001",
        visibility="public",
        status="draft",
        type="dataset",
    )

    product = NewOpenDataProduct(details)

    assert product.product_details.name == "Namespace Test"
    assert product.product_details.product_id == "namespace-001"


def test_legacy_root_import_reexports_new_odps_api():
    from odps import OpenDataProduct as LegacyOpenDataProduct
    from open_data_products.odps import OpenDataProduct as NewOpenDataProduct

    assert LegacyOpenDataProduct is NewOpenDataProduct


def test_legacy_submodule_import_reexports_new_odps_models():
    from odps.models import ProductDetails as LegacyProductDetails
    from open_data_products.odps.models import ProductDetails as NewProductDetails

    assert LegacyProductDetails is NewProductDetails


def test_legacy_submodules_remain_importable():
    module_names = [
        "odps.core",
        "odps.models",
        "odps.validation",
        "odps.validators",
        "odps.enums",
        "odps.exceptions",
        "odps.protocols",
    ]

    for module_name in module_names:
        module = importlib.import_module(module_name)
        assert module is not None
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
pytest tests/test_namespace_compatibility.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'open_data_products'`.

- [ ] **Step 3: Commit the failing tests**

Run:

```bash
git add tests/test_namespace_compatibility.py
git commit -m "test: define open data products namespace compatibility"
```

Expected: commit succeeds with only `tests/test_namespace_compatibility.py`.

---

### Task 2: Move ODPS Implementation Under `open_data_products.odps`

**Files:**
- Create: `open_data_products/__init__.py`
- Move: `odps/__init__.py` to `open_data_products/odps/__init__.py`
- Move: `odps/core.py` to `open_data_products/odps/core.py`
- Move: `odps/models.py` to `open_data_products/odps/models.py`
- Move: `odps/validation.py` to `open_data_products/odps/validation.py`
- Move: `odps/validators.py` to `open_data_products/odps/validators.py`
- Move: `odps/enums.py` to `open_data_products/odps/enums.py`
- Move: `odps/exceptions.py` to `open_data_products/odps/exceptions.py`
- Move: `odps/protocols.py` to `open_data_products/odps/protocols.py`

- [ ] **Step 1: Move existing ODPS files into the new namespace**

Run:

```bash
mkdir -p open_data_products
git mv odps open_data_products/odps
```

Expected: `open_data_products/odps` contains the existing ODPS implementation files.

- [ ] **Step 2: Create the SDK root package**

Create `open_data_products/__init__.py` with this content:

```python
"""Open Data Products Python SDK.

This package provides Python support for the OpenDataProducts.org standards
family. ODPS is available under :mod:`open_data_products.odps`.
"""

from .odps import OpenDataProduct
from .odps import ODPSValidationError
from .odps import ODPSValidator
from .odps import __version__

__all__ = [
    "OpenDataProduct",
    "ODPSValidationError",
    "ODPSValidator",
    "__version__",
]
```

- [ ] **Step 3: Run the new namespace test again**

Run:

```bash
pytest tests/test_namespace_compatibility.py::test_new_namespace_exports_existing_odps_api -q
```

Expected: PASS for `test_new_namespace_exports_existing_odps_api`; legacy import tests still fail because the compatibility package has not been recreated.

- [ ] **Step 4: Commit the namespace move**

Run:

```bash
git add open_data_products
git add -u odps
git commit -m "refactor: move odps implementation under open data products"
```

Expected: commit includes the moved implementation files and `open_data_products/__init__.py`.

---

### Task 3: Add `odps` Compatibility Wrappers

**Files:**
- Create: `odps/__init__.py`
- Create: `odps/core.py`
- Create: `odps/models.py`
- Create: `odps/validation.py`
- Create: `odps/validators.py`
- Create: `odps/enums.py`
- Create: `odps/exceptions.py`
- Create: `odps/protocols.py`

- [ ] **Step 1: Create the root compatibility wrapper**

Create `odps/__init__.py` with this content:

```python
"""Backward-compatible imports for the former ODPS-only package.

Prefer importing from ``open_data_products.odps`` in new code.
"""

from open_data_products.odps import *  # noqa: F401,F403
```

- [ ] **Step 2: Create the core compatibility wrapper**

Create `odps/core.py` with this content:

```python
"""Backward-compatible wrapper for :mod:`open_data_products.odps.core`."""

from open_data_products.odps.core import *  # noqa: F401,F403
```

- [ ] **Step 3: Create the models compatibility wrapper**

Create `odps/models.py` with this content:

```python
"""Backward-compatible wrapper for :mod:`open_data_products.odps.models`."""

from open_data_products.odps.models import *  # noqa: F401,F403
```

- [ ] **Step 4: Create the validation compatibility wrapper**

Create `odps/validation.py` with this content:

```python
"""Backward-compatible wrapper for :mod:`open_data_products.odps.validation`."""

from open_data_products.odps.validation import *  # noqa: F401,F403
```

- [ ] **Step 5: Create the validators compatibility wrapper**

Create `odps/validators.py` with this content:

```python
"""Backward-compatible wrapper for :mod:`open_data_products.odps.validators`."""

from open_data_products.odps.validators import *  # noqa: F401,F403
```

- [ ] **Step 6: Create the enums compatibility wrapper**

Create `odps/enums.py` with this content:

```python
"""Backward-compatible wrapper for :mod:`open_data_products.odps.enums`."""

from open_data_products.odps.enums import *  # noqa: F401,F403
```

- [ ] **Step 7: Create the exceptions compatibility wrapper**

Create `odps/exceptions.py` with this content:

```python
"""Backward-compatible wrapper for :mod:`open_data_products.odps.exceptions`."""

from open_data_products.odps.exceptions import *  # noqa: F401,F403
```

- [ ] **Step 8: Create the protocols compatibility wrapper**

Create `odps/protocols.py` with this content:

```python
"""Backward-compatible wrapper for :mod:`open_data_products.odps.protocols`."""

from open_data_products.odps.protocols import *  # noqa: F401,F403
```

- [ ] **Step 9: Run namespace compatibility tests**

Run:

```bash
pytest tests/test_namespace_compatibility.py -q
```

Expected: PASS for all namespace compatibility tests.

- [ ] **Step 10: Run the existing ODPS test suite**

Run:

```bash
pytest tests -q
```

Expected: Existing behavior should be unchanged. If failures mention expected schema/version values such as v4.0 versus v4.1, record them as pre-existing version expectation drift and do not fix them in this task unless they are caused by imports.

- [ ] **Step 11: Commit the compatibility wrappers**

Run:

```bash
git add odps
git commit -m "feat: keep odps compatibility imports"
```

Expected: commit includes only wrapper files under `odps/`.

---

### Task 4: Update Packaging Metadata

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update the project metadata**

In `pyproject.toml`, change:

```toml
name = "odps-python"
description = "High-performance Python library for Open Data Product Specification (ODPS) v4.1 with ProductStrategy, AI integration, caching, validation, and international standards compliance"
```

to:

```toml
name = "open-data-products"
description = "Python SDK for the OpenDataProducts.org standards family, including ODPS data products and future ODPV, ODPC, and ODPG support"
```

- [ ] **Step 2: Update project keywords**

Replace the existing `keywords` array with:

```toml
keywords = [
    "open-data",
    "data-product",
    "open-data-products",
    "odps",
    "odpv",
    "odpc",
    "odpg",
    "specification",
    "validation",
    "vocabulary",
    "catalog",
    "graph",
    "iso-standards",
    "rfc",
    "type-safety",
]
```

- [ ] **Step 3: Update package discovery**

Replace:

```toml
[tool.setuptools]
packages = ["odps"]
```

with:

```toml
[tool.setuptools]
packages = [
    "open_data_products",
    "open_data_products.odps",
    "odps",
]
```

- [ ] **Step 4: Update dynamic version source**

Replace:

```toml
[tool.setuptools.dynamic]
version = {attr = "odps.__version__"}
```

with:

```toml
[tool.setuptools.dynamic]
version = {attr = "open_data_products.__version__"}
```

- [ ] **Step 5: Update coverage source**

Replace:

```toml
[tool.coverage.run]
source = ["odps"]
```

with:

```toml
[tool.coverage.run]
source = ["open_data_products", "odps"]
```

- [ ] **Step 6: Verify package metadata can be read**

Run:

```bash
python -m pip install -e .
```

Expected: editable install succeeds and reports package name `open-data-products`.

- [ ] **Step 7: Verify imports from installed package**

Run:

```bash
python -c "from open_data_products.odps import OpenDataProduct; from odps import OpenDataProduct as Legacy; assert OpenDataProduct is Legacy; print('imports ok')"
```

Expected output:

```text
imports ok
```

- [ ] **Step 8: Run namespace compatibility tests**

Run:

```bash
pytest tests/test_namespace_compatibility.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit packaging updates**

Run:

```bash
git add pyproject.toml
git commit -m "build: rename package metadata to open data products"
```

Expected: commit includes only `pyproject.toml`.

---

### Task 5: Update Documentation For New Namespace

**Files:**
- Modify: `README.md`
- Modify: `docs/API.md`

- [ ] **Step 1: Update README package title and install command**

In `README.md`, replace the title:

```markdown
# ODPS Python Library
```

with:

```markdown
# Open Data Products Python SDK
```

Replace:

```bash
pip install odps-python
```

with:

```bash
pip install open-data-products
```

- [ ] **Step 2: Add a compatibility note to README**

Add this paragraph after the installation commands:

```markdown
Existing ODPS users can continue importing from `odps` during the compatibility period. New code should prefer `open_data_products.odps` because the SDK is expanding to support the broader OpenDataProducts.org standards family.
```

- [ ] **Step 3: Update the first README import example**

Replace:

```python
from odps import OpenDataProduct
from odps.models import (
```

with:

```python
from open_data_products.odps import OpenDataProduct
from open_data_products.odps.models import (
```

- [ ] **Step 4: Add an API documentation compatibility note**

In `docs/API.md`, add this section near the top, after the opening heading:

```markdown
## Package Namespace

New code should import ODPS APIs from `open_data_products.odps`:

```python
from open_data_products.odps import OpenDataProduct
from open_data_products.odps.models import ProductDetails
```

The historical `odps` namespace remains available for backward compatibility:

```python
from odps import OpenDataProduct
from odps.models import ProductDetails
```
```

- [ ] **Step 5: Run documentation import smoke test**

Run:

```bash
python -c "from open_data_products.odps import OpenDataProduct; from open_data_products.odps.models import ProductDetails; print(OpenDataProduct.__name__, ProductDetails.__name__)"
```

Expected output:

```text
OpenDataProduct ProductDetails
```

- [ ] **Step 6: Commit documentation updates**

Run:

```bash
git add README.md docs/API.md
git commit -m "docs: document open data products namespace"
```

Expected: commit includes only documentation changes.

---

### Task 6: Final Verification

**Files:**
- No new files.
- Verify all changes from Tasks 1-5.

- [ ] **Step 1: Check working tree**

Run:

```bash
git status --short
```

Expected: no output.

- [ ] **Step 2: Run namespace tests**

Run:

```bash
pytest tests/test_namespace_compatibility.py -q
```

Expected: PASS.

- [ ] **Step 3: Run full test suite**

Run:

```bash
pytest tests -q
```

Expected: PASS. If failures are unrelated to namespace migration and existed before this work, capture the failing test names and error messages in the final implementation note.

- [ ] **Step 4: Verify distribution build metadata**

Run:

```bash
python -m build
```

Expected: build succeeds and creates artifacts under `dist/` with `open_data_products` package content.

- [ ] **Step 5: Inspect package list in built wheel**

Run:

```bash
python -m zipfile -l dist/*.whl
```

Expected: output includes:

```text
open_data_products/__init__.py
open_data_products/odps/__init__.py
open_data_products/odps/core.py
odps/__init__.py
odps/models.py
```

- [ ] **Step 6: Commit final verification notes only if files changed**

If no files changed during verification, do not commit.

If documentation or metadata needed a small verification fix, run:

```bash
git add README.md docs/API.md pyproject.toml
git commit -m "chore: finalize open data products namespace migration"
```

Expected: commit includes only final fixes required by verification.

---

## Self-Review

### Spec Coverage

- Package identity moves toward `open-data-products`: Task 4.
- Python namespace becomes `open_data_products`: Tasks 1 and 2.
- Existing `odps` imports stay compatible: Tasks 1 and 3.
- ODPS implementation moves under `open_data_products.odps`: Task 2.
- Packaging includes both namespaces: Task 4.
- Documentation points users to the new namespace: Task 5.
- Tests prove old and new imports work: Tasks 1, 3, and 6.

### Deferred Spec Items

- ODPV script port is intentionally deferred to the next plan.
- ODPC support is intentionally deferred until after ODPV tooling.
- ODPG support is intentionally deferred until after ODPC.
- `odp` CLI is intentionally deferred until at least one non-ODPS module is present.

### Placeholder Scan

The plan contains no placeholder markers or unspecified implementation steps. Each code-changing task includes exact files, exact code blocks, commands, and expected results.
