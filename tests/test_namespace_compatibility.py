"""Tests for open_data_products namespace and odps compatibility imports."""

import importlib


def test_new_namespace_exports_existing_odps_api():
    from open_data_products import OpenDataProduct as RootOpenDataProduct
    from open_data_products.odps import OpenDataProduct as NewOpenDataProduct

    assert RootOpenDataProduct is NewOpenDataProduct


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
        assert module.__name__ == module_name
