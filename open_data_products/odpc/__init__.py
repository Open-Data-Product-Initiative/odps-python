"""Open Data Product Catalog (ODPC) namespace."""

SPEC_ID = "odpc"
SPEC_NAME = "Open Data Product Catalog"

from .catalog import (
    CatalogValidationResult,
    collect_ids,
    count_items,
    explain_catalog,
    load_catalog,
    load_object_records,
    load_schema,
    render_object_records,
    search_objects,
    validate_catalog,
)

__all__ = [
    "SPEC_ID",
    "SPEC_NAME",
    "CatalogValidationResult",
    "collect_ids",
    "count_items",
    "explain_catalog",
    "load_catalog",
    "load_object_records",
    "load_schema",
    "render_object_records",
    "search_objects",
    "validate_catalog",
]
