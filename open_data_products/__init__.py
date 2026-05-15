"""Open Data Products Python SDK.

This package provides Python support for the OpenDataProducts.org standards
family. Each standard lives in its own namespace:

- :mod:`open_data_products.odps`
- :mod:`open_data_products.odpc`
- :mod:`open_data_products.odpg`
- :mod:`open_data_products.odpv`
"""

__version__ = "0.2.0"

from . import odpc
from . import odpg
from . import odps
from . import odpv
from .agent import (
    detect_document,
    explain_document,
    explain_product,
    explain_vocabulary,
    load_document,
    resolve_references,
    validate_document,
)
from .pricing import pricing_to_402
from .resources import get_resource, list_resources
from .results import Reference, Resource, ValidationResult
from .summary import load_summary

__all__ = [
    "__version__",
    "odpc",
    "odpg",
    "odps",
    "odpv",
    "Reference",
    "Resource",
    "ValidationResult",
    "detect_document",
    "explain_document",
    "explain_product",
    "explain_vocabulary",
    "get_resource",
    "list_resources",
    "load_document",
    "load_summary",
    "pricing_to_402",
    "resolve_references",
    "validate_document",
]
