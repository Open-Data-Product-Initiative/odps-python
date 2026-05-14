#!/usr/bin/env python3
"""
Advanced ODPS Python Library Features Examples (ODPS v4.1)

This script demonstrates advanced features including:
- Protocol compliance checking
- Custom validation rules
- Performance monitoring
- Complex component configurations
- Multilingual support

Note: For v4.1-specific features (ProductStrategy, KPI, AI agents),
see odps_v41_example.py
"""

from open_data_products.odps import OpenDataProduct, ProductDetails
from open_data_products.odps.models import *
from open_data_products.odps.validation import ODPSValidationFramework, ValidationRule
from open_data_products.odps.protocols import (
    is_validatable,
    validate_protocol_compliance,
)
from open_data_products.odps.exceptions import ODPSValidationError, create_field_error
from open_data_products.odps.enums import (
    ProductStatus,
    ProductVisibility,
    DataContractType,
)
import time
from typing import List, Any


class CustomBusinessRuleValidator(ValidationRule):
    """Custom validator implementing business-specific rules."""

    def validate(self, product: "OpenDataProduct") -> List[str]:
        """Validate custom business rules."""
        errors = []

        # Rule 1: Production products must have data access
        if (
            product.product_details.status == ProductStatus.PRODUCTION.value
            and product.data_access is None
        ):
            errors.append("Production products must define data access methods")

        # Rule 2: Commercial products must have pricing
        if (
            product.license
            and product.license.scope_of_use == "commercial"
            and product.pricing_plans is None
        ):
            errors.append("Commercial products must define pricing plans")

        # Rule 3: Organization visibility requires data holder
        if (
            product.product_details.visibility == ProductVisibility.ORGANISATION.value
            and product.data_holder is None
        ):
            errors.append("Organization-level products must specify data holder")

        return errors


def protocol_compliance_demo():
    """Demonstrate protocol-based validation and compliance checking."""
    print("=== Protocol Compliance Demo ===")

    # Create a product
    details = ProductDetails(
        name="Protocol Demo Product",
        product_id="protocol-001",
        visibility="public",
        status="production",
        type="dataset",
    )

    product = OpenDataProduct(details)

    # Check protocol compliance
    print("Checking protocol compliance:")
    print(f"   Is validatable: {is_validatable(product)}")

    # Detailed protocol compliance
    compliance_errors = validate_protocol_compliance(product, "ODPSDocumentProtocol")
    if compliance_errors:
        print(f"   Protocol errors: {compliance_errors}")
    else:
        print("   ✅ Fully compliant with ODPSDocumentProtocol")

    # Check component protocols
    component_results = product.check_component_protocols()
    print(f"   Component protocol compliance: {component_results}")

    return product


def custom_validation_demo():
    """Demonstrate custom validation rules and framework usage."""
    print("\n=== Custom Validation Demo ===")

    # Create validation framework with custom rule
    framework = ODPSValidationFramework()
    custom_validator = CustomBusinessRuleValidator()
    framework.add_validator(custom_validator)

    # Test product that should fail custom validation
    details = ProductDetails(
        name="Production Dataset",
        product_id="prod-001",
        visibility="organisation",  # British spelling per ODPS spec
        status=ProductStatus.PRODUCTION.value,  # Using enum
        type="dataset",
    )

    product = OpenDataProduct(details)
    product.add_license("commercial")  # Commercial but no pricing
    # Note: No data_access or data_holder added

    # Test custom validation
    try:
        errors = framework.validate(product)
        if errors:
            print(f"❌ Custom validation failed with {len(errors)} errors:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ All custom validations passed")
    except Exception as e:
        print(f"❌ Validation error: {e}")

    # Fix the issues and revalidate
    print("\nFixing issues and revalidating:")

    # Add required components
    product.data_holder = DataHolder(name="Data Corp", email="info@datacorp.com")

    api_access = DataAccessMethod(
        name={"en": "API Access"},
        output_port_type="API",
        access_url="https://api.example.com/data",
    )
    product.add_data_access(api_access)

    pricing = PricingPlans(
        plans=[PricingPlan(name="Standard Plan", price_currency="USD", price=99.99)]
    )
    product.pricing_plans = pricing

    # Revalidate
    errors = framework.validate(product)
    if errors:
        print(f"❌ Still failing: {errors}")
    else:
        print("✅ All custom validations now pass!")


def multilingual_support_demo():
    """Demonstrate multilingual field support."""
    print("\n=== Multilingual Support Demo ===")

    # Create product with multilingual elements
    details = ProductDetails(
        name="Global Weather Dataset",
        product_id="weather-global-001",
        visibility="public",
        status="production",
        type="dataset",
        description="Weather data available in multiple languages",
        language=["en", "fr", "de", "es"],  # Multi-language support
    )

    product = OpenDataProduct(details)

    # Add multilingual data access
    multilingual_access = DataAccessMethod(
        name={
            "en": "Weather API",
            "fr": "API Météo",
            "de": "Wetter-API",
            "es": "API del Tiempo",
        },
        description={
            "en": "Real-time weather data access",
            "fr": "Accès aux données météorologiques en temps réel",
            "de": "Echtzeit-Wetterdaten-Zugang",
            "es": "Acceso a datos meteorológicos en tiempo real",
        },
        output_port_type="API",
        format="JSON",
        access_url="https://weather-api.global.com/v1",
    )

    product.add_data_access(multilingual_access)

    # Add multilingual pricing
    multilingual_pricing = PricingPlans(
        plans=[
            PricingPlan(
                name={
                    "en": "Premium Weather Access",
                    "fr": "Accès Météo Premium",
                    "de": "Premium Wetter Zugang",
                    "es": "Acceso Premium al Tiempo",
                },
                price_currency="EUR",
                price=29.99,
                billing_duration="monthly",
            )
        ]
    )

    product.pricing_plans = multilingual_pricing

    # Validate multilingual support
    try:
        product.validate()
        print("✅ Multilingual product validated successfully")

        # Show JSON output with multilingual fields
        json_output = product.to_json()
        print("Sample multilingual JSON structure:")
        # Extract just the multilingual parts for display
        import json

        data = json.loads(json_output)
        if "dataAccess" in data["product"]:
            access_name = data["product"]["dataAccess"]["default"].get("name", {})
            print(f"   API names: {access_name}")

    except ODPSValidationError as e:
        print(f"❌ Multilingual validation failed: {e}")


def performance_monitoring_demo():
    """Demonstrate performance monitoring and optimization features."""
    print("\n=== Performance Monitoring Demo ===")

    # Create a complex product for performance testing
    details = ProductDetails(
        name="Performance Benchmark Dataset",
        product_id="perf-benchmark-001",
        visibility="public",
        status="production",
        type="dataset",
        description="Large dataset for performance testing",
        categories=["benchmark", "performance", "testing"],
        tags=["large-scale", "optimization", "metrics"],
        created="2024-01-01T00:00:00Z",
        updated="2024-08-09T12:00:00Z",
    )

    product = OpenDataProduct(details)

    # Add multiple components to increase complexity
    product.data_holder = DataHolder(
        name="Performance Testing Corp",
        email="perf@testing.com",
        url="https://testing.com",
        phone_number="+12025551234",
    )

    product.add_license(
        scope_of_use="research",
        geographical_area=["US", "EU", "CA", "AU", "JP"],
        permanent=True,
    )

    # Multiple data access methods
    api_method = DataAccessMethod(
        name={"en": "High-Performance API"},
        output_port_type="API",
        access_url="https://api.testing.com/v1/data",
        format="JSON",
    )
    product.add_data_access(api_method)

    # Performance testing
    iterations = 10
    validation_times = []
    serialization_times = []

    print(f"Running {iterations} performance iterations...")

    for i in range(iterations):
        # Test validation performance
        start = time.time()
        product.validate()
        validation_time = time.time() - start
        validation_times.append(validation_time)

        # Test serialization performance
        start = time.time()
        json_output = product.to_json()
        serialization_time = time.time() - start
        serialization_times.append(serialization_time)

        # Invalidate cache occasionally to test cache effectiveness
        if i % 3 == 0:
            product._invalidate_cache()

    # Performance statistics
    avg_validation = sum(validation_times) / len(validation_times)
    avg_serialization = sum(serialization_times) / len(serialization_times)

    # Compare with and without cache
    first_validation = validation_times[0]  # No cache
    cached_validations = validation_times[1:3]  # Should be cached
    avg_cached = sum(cached_validations) / len(cached_validations)

    print(f"\n📊 Performance Results:")
    print(f"   Average validation time: {avg_validation:.4f}s")
    print(f"   Average serialization time: {avg_serialization:.4f}s")
    print(f"   First validation (no cache): {first_validation:.4f}s")
    print(f"   Cached validation average: {avg_cached:.4f}s")
    if avg_cached > 0:
        speedup = first_validation / avg_cached
        print(f"   🚀 Cache speedup: {speedup:.1f}x")


def complex_document_creation():
    """Create a complex ODPS document with all components."""
    print("\n=== Complex Document Creation ===")

    # Create comprehensive product details
    details = ProductDetails(
        name="Enterprise Customer Intelligence Platform",
        product_id="ent-cip-v3.2",
        visibility=ProductVisibility.ORGANISATION.value,  # British spelling per ODPS spec
        status=ProductStatus.PRODUCTION.value,
        type="platform",
        value_proposition="Complete customer intelligence solution with AI-powered insights",
        description="Comprehensive customer data platform with advanced analytics",
        categories=["customer-intelligence", "analytics", "ai-ml"],
        tags=["enterprise", "customer-data", "machine-learning", "insights"],
        brand="DataCorp Intelligence",
        keywords=["customer", "analytics", "intelligence", "platform"],
        themes=["digital-transformation", "data-driven-decisions"],
        geography="Global",
        language=["en", "fr", "de"],
        homepage="https://datacorp.com/cip",
        logo_url="https://datacorp.com/assets/cip-logo.png",
        created="2023-06-01T00:00:00Z",
        updated="2024-08-09T10:30:00Z",
        product_series="Customer Intelligence",
        standards=["ISO27001", "SOC2", "GDPR"],
        product_version="3.2.1",
        version_notes="Enhanced AI capabilities and GDPR compliance updates",
        issues="https://datacorp.com/cip/support",
        content_sample="https://datacorp.com/cip/sample-data",
        brand_slogan="Intelligence at Scale",
        output_file_formats=["JSON", "CSV", "Parquet", "Avro"],
    )

    product = OpenDataProduct(details)

    # Add comprehensive data contract
    product.data_contract = DataContract(
        id="cip-contract-v3.2",
        type=DataContractType.ODCS.value,
        contract_version="3.2",
        contract_url="https://datacorp.com/contracts/cip-v3.2.yaml",
        spec={
            "version": "3.2",
            "schema": {
                "customers": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "created_at": {"type": "string", "format": "date-time"},
                    },
                }
            },
        },
    )

    # Add comprehensive SLA
    product.add_sla(
        profiles={
            "default": {
                "availability": "99.9%",
                "response_time": "< 100ms",
                "throughput": "10000 requests/second",
                "support": "24/7 enterprise support",
            }
        }
    )

    # Add detailed data holder
    product.data_holder = DataHolder(
        name="DataCorp Intelligence Division",
        email="cip-support@datacorp.com",
        url="https://datacorp.com/intelligence",
        phone_number="+12025551234",
        address="123 Intelligence Ave, Data City, DC 12345",
        business_identifiers=["DUNS:123456789", "VAT:US123456789"],
        contact_person="Sarah Johnson",
        contact_phone="+12025551235",
        contact_email="sarah.johnson@datacorp.com",
        address_street="123 Intelligence Ave",
        address_city="Data City",
        address_state="DC",
        address_postal_code="12345",
        address_country="US",
        organizational_description="Leading provider of enterprise customer intelligence solutions",
    )

    # Add comprehensive license
    product.add_license(
        scope_of_use="commercial",
        geographical_area=["US", "CA", "EU", "UK", "AU"],
        permanent=False,
        exclusive=False,
        right_to_sublicense=True,
        right_to_modify=False,
        valid_from="2024-01-01T00:00:00Z",
        valid_until="2025-12-31T23:59:59Z",
        license_grant="Comprehensive enterprise usage rights",
        license_name="DataCorp Enterprise License v2.0",
        license_url="https://datacorp.com/licenses/enterprise-v2.0",
    )

    # Add multiple data access methods
    api_method = DataAccessMethod(
        name={"en": "REST API"},
        description={"en": "High-performance RESTful API with OAuth2"},
        output_port_type="API",
        format="JSON",
        access_url="https://api.datacorp.com/cip/v3",
        authentication_method="OAUTH2",
        specs_url="https://api.datacorp.com/cip/openapi.yaml",
        documentation_url="https://docs.datacorp.com/cip/api",
    )

    product.add_data_access(api_method)

    # Add comprehensive pricing
    product.pricing_plans = PricingPlans(
        plans=[
            PricingPlan(
                name="Enterprise Standard",
                price_currency="USD",
                price=999.00,
                billing_duration="monthly",
                unit="platform_access",
                max_transactions_per_month=1000000,
                min_price=999.00,
                max_price=4999.00,
                valid_from="2024-01-01",
                valid_to="2024-12-31",
            ),
            PricingPlan(
                name="Enterprise Premium",
                price_currency="USD",
                price=2999.00,
                billing_duration="monthly",
                unit="platform_access",
                max_transactions_per_month=5000000,
                min_price=2999.00,
                max_price=9999.00,
            ),
        ]
    )

    # Add extensions
    product.extensions = SpecificationExtensions()
    product.extensions.add_extension("x-datacorp-tier", "enterprise")
    product.extensions.add_extension("x-support-level", "premium")
    product.extensions.add_extension(
        "x-deployment-regions", ["us-east", "eu-west", "ap-south"]
    )

    # Validate complex document
    try:
        product.validate()
        print("✅ Complex enterprise document validated successfully")
        print(f"   Compliance level: {product.compliance_level}")
        print(f"   Component count: {product.component_count}")
        print(f"   Production ready: {product.is_production_ready}")

        # Save comprehensive document
        product.save("examples/enterprise_product.json")
        print("   💾 Saved as enterprise_product.json")

        return product

    except ODPSValidationError as e:
        print(f"❌ Complex validation failed: {e}")
        return None


def main():
    """Run all advanced feature demonstrations."""
    print("ODPS Python Library - Advanced Features")
    print("=======================================")

    # Protocol compliance
    protocol_product = protocol_compliance_demo()

    # Custom validation
    custom_validation_demo()

    # Multilingual support
    multilingual_support_demo()

    # Performance monitoring
    performance_monitoring_demo()

    # Complex document creation
    complex_product = complex_document_creation()

    print("\n🎉 All advanced examples completed successfully!")
    print("\nAdvanced features demonstrated:")
    print("✅ Protocol compliance checking")
    print("✅ Custom validation rules")
    print("✅ Multilingual support")
    print("✅ Performance monitoring")
    print("✅ Complex enterprise document creation")
    print("✅ Comprehensive component configuration")


if __name__ == "__main__":
    main()
