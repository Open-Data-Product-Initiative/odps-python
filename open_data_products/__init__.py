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

__all__ = [
    "__version__",
    "odpc",
    "odpg",
    "odps",
    "odpv",
]
