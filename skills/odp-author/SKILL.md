---
name: odp-author
description: Author or edit Open Data Products documents (ODPS product specs, ODPC catalogs, ODPG graphs, ODPV vocabularies). Knows the v4.1 field names, required vs optional, enum vocabularies, and the conventional file layout.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
---

# Open Data Products: Author

Activate when the user asks to create, draft, or edit an ODP document.

## Workflow

1. Decide which spec applies:
   - **ODPS** — a single data product description
   - **ODPC** — a catalog grouping many products
   - **ODPG** — a graph of relationships across products/objectives/KPIs
   - **ODPV** — a vocabulary of terms used by the other three
2. Start from a bundled example. Discover paths via:
   ```bash
   open-data-products resources --json
   ```
3. Edit the YAML. Required fields for ODPS: `productID`, `name`, `status`,
   `visibility`, `type`. Use the canonical `schema:` URL.
4. Validate after every meaningful change:
   ```bash
   open-data-products validate path/to/file.yaml
   ```

## Enum vocabularies

These are the legal enum values (full per-value descriptions are in
`open_data_products/odps/enums.py` — render with `ProductStatus.describe()`):

- `status`: announcement, draft, development, testing, acceptance,
  production, sunset, retired
- `visibility`: private, invitation, organisation, dataspace, public
- `type`: raw data, derived data, dataset, reports, analytic view,
  3D visualisation, algorithm, decision support, automated decision-making,
  data-enhanced product, data-driven service, data-enabled performance,
  bi-directional

## Pricing

When a product has a `pricingPlans` block, the `pricing_to_402` helper can
render the corresponding HTTP 402 envelope:

```python
from open_data_products import load_document, pricing_to_402
product = load_document("premium.yaml")
envelope = pricing_to_402(product)  # {"status": 402, "headers": {...}}
```

## Output

Always validate before reporting "done." Show the resulting `valid: true`
line so the user has confirmation, not just an assertion.
