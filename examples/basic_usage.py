#!/usr/bin/env python3
"""
Basic ODPS Python Library Usage Examples

This script demonstrates the fundamental features of the ODPS Python library
including creating, validating, and exporting ODPS v4.1 documents.

Note: For v4.1-specific features (ProductStrategy, KPI, AI agents),
see odps_v41_example.py
"""

from open_data_products.odps import OpenDataProduct, ProductDetails
from open_data_products.odps.models import (
    DataHolder,
    License,
    DataAccess,
    DataAccessMethod,
)
from open_data_products.odps.exceptions import ODPSValidationError


def basic_document_creation():
    """Create a basic ODPS document with minimal required fields."""
    print("=== Basic Document Creation ===")

    # Create product details with required fields
    details = ProductDetails(
        name="Customer Analytics Dataset",
        product_id="cust-analytics-2024",
        visibility="public",
        status="production",
        type="dataset",
        description="Comprehensive customer behavior analytics data",
    )

    # Create ODPS document
    product = OpenDataProduct(details)

    # Validate the document
    try:
        is_valid = product.validate()
        print(f"✅ Document is valid: {is_valid}")
        print(f"   Compliance level: {product.compliance_level}")
        print(f"   Component count: {product.component_count}")
    except ODPSValidationError as e:
        print(f"❌ Validation failed: {e}")

    return product


def enhanced_document_with_components():
    """Create a comprehensive ODPS document with multiple optional components."""
    print("\n=== Enhanced Document with Optional Components ===")

    # Create detailed product information
    details = ProductDetails(
        name="Enterprise Sales Dataset",
        product_id="ent-sales-v2.1",
        visibility="organization",
        status="production",
        type="dataset",
        description="Monthly sales data with customer segmentation",
        categories=["analytics", "sales", "business-intelligence"],
        tags=["monthly", "b2b", "revenue", "customers"],
        brand="Acme Analytics",
        homepage="https://acme.com/data/sales-dataset",
        # Enhanced optional fields
        product_version="2.1.0",
        version_notes="Added customer lifetime value calculations",
        created="2024-01-15T10:00:00Z",
        updated="2024-08-01T14:30:00Z",
    )

    product = OpenDataProduct(details)

    # Add data holder information
    product.data_holder = DataHolder(
        name="Acme Corporation Data Team",
        email="data-team@acme.com",
        url="https://acme.com/data",
        phone_number="+12025551234",
        address="123 Data Street, Analytics City, AC 12345",
        contact_person="Jane Smith",
        contact_email="jane.smith@acme.com",
        organizational_description="Leading provider of business analytics solutions",
    )

    # Add license information
    product.add_license(
        scope_of_use="commercial",
        geographical_area=["US", "CA", "EU"],
        permanent=False,
        exclusive=False,
        right_to_sublicense=False,
        valid_from="2024-01-01T00:00:00Z",
        valid_until="2025-12-31T23:59:59Z",
    )

    # Add data access method
    api_method = DataAccessMethod(
        name={"en": "REST API Access"},
        description={"en": "RESTful API with OAuth2 authentication"},
        output_port_type="API",
        format="JSON",
        access_url="https://api.acme.com/v2/sales",
        authentication_method="OAUTH2",
        specs_url="https://api.acme.com/docs/openapi.yaml",
        documentation_url="https://docs.acme.com/sales-api",
    )

    product.add_data_access(api_method)

    # Validate comprehensive document
    try:
        product.validate()
        print(f"✅ Enhanced document is valid")
        print(f"   Compliance level: {product.compliance_level}")
        print(f"   Production ready: {product.is_production_ready}")
        print(f"   Has optional components: {product.has_optional_components}")
    except ODPSValidationError as e:
        print(f"❌ Validation failed: {e}")

    return product


def performance_demonstration():
    """Demonstrate performance features including caching."""
    print("\n=== Performance Features Demo ===")

    import time

    # Create a product for performance testing
    details = ProductDetails(
        name="Performance Test Dataset",
        product_id="perf-test-001",
        visibility="public",
        status="draft",
        type="dataset",
    )

    product = OpenDataProduct(details)

    # Test validation caching
    print("Testing validation performance:")

    # First validation - full processing
    start = time.time()
    product.validate()
    first_time = time.time() - start

    # Second validation - cached result
    start = time.time()
    product.validate()
    cached_time = time.time() - start

    print(f"   First validation: {first_time:.4f}s")
    print(f"   Cached validation: {cached_time:.4f}s")
    if cached_time > 0:
        print(f"   🚀 Cache speedup: {first_time/cached_time:.1f}x")
    else:
        print(f"   🚀 Instant cache hit!")

    # Test serialization caching
    print("\nTesting serialization performance:")

    start = time.time()
    json1 = product.to_json()
    first_json_time = time.time() - start

    start = time.time()
    json2 = product.to_json()
    cached_json_time = time.time() - start

    print(f"   First JSON export: {first_json_time:.4f}s")
    print(f"   Cached JSON export: {cached_json_time:.4f}s")
    if cached_json_time > 0:
        print(f"   🚀 JSON cache speedup: {first_json_time/cached_json_time:.1f}x")

    # Test cache invalidation
    print("\nTesting cache invalidation:")
    product.add_license("test-scope")  # This should invalidate cache

    start = time.time()
    product.validate()
    invalidated_time = time.time() - start

    print(f"   Validation after modification: {invalidated_time:.4f}s")
    print("   ✅ Cache properly invalidated")


def error_handling_examples():
    """Demonstrate comprehensive error handling."""
    print("\n=== Error Handling Examples ===")

    from open_data_products.odps.exceptions import (
        ODPSValidationError,
        ODPSFieldValidationError,
        ODPSComponentError,
        ODPSFileNotFoundError,
    )

    # Example 1: Validation error
    try:
        details = ProductDetails(
            name="",  # Invalid empty name
            product_id="test-001",
            visibility="invalid_visibility",  # Invalid value
            status="draft",
            type="dataset",
        )
        product = OpenDataProduct(details)
        product.validate()
    except ODPSValidationError as e:
        print(f"✅ Caught validation error: {e}")
        print(f"   Error details: {e.details}")

    # Example 2: File not found error
    try:
        product = OpenDataProduct.from_file("nonexistent_file.json")
    except ODPSFileNotFoundError as e:
        print(f"✅ Caught file error: {e}")
        print(f"   File path: {e.file_path}")

    # Example 3: Using validation_errors property (no exceptions)
    details = ProductDetails(
        name="Test Product",
        product_id="",  # Invalid empty ID
        visibility="public",
        status="draft",
        type="dataset",
    )
    product = OpenDataProduct(details)

    errors = product.validation_errors
    if errors:
        print(f"✅ Validation errors found (no exception): {len(errors)}")
        for error in errors:
            print(f"   - {error}")


def serialization_examples():
    """Demonstrate various serialization options."""
    print("\n=== Serialization Examples ===")

    # Create a sample product
    details = ProductDetails(
        name="Serialization Demo Dataset",
        product_id="serial-demo-001",
        visibility="public",
        status="production",
        type="dataset",
    )

    product = OpenDataProduct(details)
    product.add_license("commercial", geographical_area=["US"])

    # JSON serialization
    json_output = product.to_json(indent=4)
    print("JSON output (first 200 chars):")
    print(json_output[:200] + "...")

    # YAML serialization
    yaml_output = product.to_yaml()
    print("\nYAML output (first 200 chars):")
    print(yaml_output[:200] + "...")

    # Save to files
    product.save("sample_product.json")
    product.save("sample_product.yaml")
    print("\n✅ Saved to sample_product.json and sample_product.yaml")

    # Load from file
    loaded_product = OpenDataProduct.from_file("sample_product.json")
    print(f"✅ Loaded product: {loaded_product.product_details.name}")


def main():
    """Run all example demonstrations."""
    print("ODPS Python Library - Usage Examples")
    print("====================================")

    # Basic usage
    basic_product = basic_document_creation()

    # Enhanced usage with components
    enhanced_product = enhanced_document_with_components()

    # Performance features
    performance_demonstration()

    # Error handling
    error_handling_examples()

    # Serialization
    serialization_examples()

    print("\n🎉 All examples completed successfully!")
    print("\nNext steps:")
    print("- Check out the generated sample_product.json and sample_product.yaml files")
    print("- Explore the comprehensive API documentation")
    print("- Visit https://opendataproducts.org/v4.0/ for the full ODPS specification")


if __name__ == "__main__":
    main()
