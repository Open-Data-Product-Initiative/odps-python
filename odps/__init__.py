"""Backward-compatible imports for the former ODPS-only package.

Prefer importing from ``open_data_products.odps`` in new code.
"""

from open_data_products.odps import *  # noqa: F401,F403
from open_data_products.odps import __version__  # noqa: F401
