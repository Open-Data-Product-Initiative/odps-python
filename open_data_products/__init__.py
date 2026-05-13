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
