"""
Example usage of the ODPS Python library with full standards compliance (ODPS v4.1)

This example demonstrates the ODPS library with international standards compliance.
For v4.1-specific features (ProductStrategy, KPI, AI agents), see odps_v41_example.py
"""

from open_data_products.odps import OpenDataProduct, ODPSValidationError
from open_data_products.odps.models import (
    ProductDetails,
    License,
    DataAccessMethod,
    DataHolder,
    PricingPlan,
    PricingPlans,
)


def main():
    # Create a new ODPS document with international standards
    print("Creating a new Open Data Product with standards compliance...")

    product_details = ProductDetails(
        name="Weather Data API",
        product_id="weather-api-v1",
        visibility="public",
        status="production",
        type="dataset",
        description="Real-time weather data from global monitoring stations",
        categories=["weather", "environmental"],
        tags=["api", "real-time", "global"],
        value_proposition="Access to accurate, real-time weather data for applications",
        language=["en", "fr", "es"],  # ISO 639-1 language codes
        homepage="https://weather-api.example.com",  # RFC 3986 URI
    )

    # Create ODPS instance
    odp = OpenDataProduct(product_details)

    # Add data access with required default method and multilingual support
    default_access = DataAccessMethod(
        name={
            "en": "Weather REST API",
            "fr": "API REST Météo",
            "es": "API REST del Clima",
        },
        description={
            "en": "Primary API access for weather data",
            "fr": "Accès API principal pour les données météo",
            "es": "Acceso API principal para datos meteorológicos",
        },
        output_port_type="API",
        format="JSON",
        access_url="https://api.weather.example.com/data",  # RFC 3986 URI
        documentation_url="https://docs.weather.example.com",  # RFC 3986 URI
        specs_url="https://api.weather.example.com/spec",  # RFC 3986 URI
    )
    odp.add_data_access(default_access)

    # Add data holder with validated contact information
    odp.data_holder = DataHolder(
        name="Weather Data Corp",
        email="contact@weather-data.example.com",  # RFC 5322 email
        phone_number="+12125551234",  # E.164 phone number
        address="123 Weather St, Climate City, NY 10001",
    )

    # Add license with ISO 8601 date validation
    odp.license = License(
        scope_of_use="commercial",
        geographical_area=["US", "CA", "MX"],  # ISO 3166-1 alpha-2 country codes
        license_name="MIT License",
        valid_from="2024-01-01",  # ISO 8601 date
        valid_until="2025-12-31T23:59:59Z",  # ISO 8601 datetime
    )

    # Add pricing plans with ISO 4217 currency codes
    odp.pricing_plans = PricingPlans(
        plans=[
            PricingPlan(
                name="Basic Plan",
                price_currency="USD",  # ISO 4217 currency code
                price=9.99,
                billing_duration="monthly",
                max_transactions_per_month=10000,
            ),
            PricingPlan(
                name="Enterprise Plan",
                price_currency="USD",  # ISO 4217 currency code
                price=99.99,
                billing_duration="monthly",
                max_transactions_per_month=1000000,
            ),
        ]
    )

    odp.add_data_contract(
        contract_url="https://api.weather.example.com/contract",  # RFC 3986 URI
        spec={
            "format": "OpenAPI 3.0",
            "authentication": "Bearer Token",
            "rate_limit": "1000 requests/hour",
        },
    )

    # Comprehensive validation with international standards
    print("\nValidating with international standards...")
    try:
        odp.validate()
        print("✓ ODPS document is valid with full standards compliance:")
        print("  • ISO 639-1: Language codes validated")
        print("  • ISO 3166-1: Country codes validated")
        print("  • ISO 4217: Currency codes validated")
        print("  • ISO 8601: Date/time formats validated")
        print("  • E.164: Phone number format validated")
        print("  • RFC 5322: Email format validated")
        print("  • RFC 3986: URI/URL formats validated")
        print("  • ODPS v4.0: dataAccess.default requirement enforced")
    except ODPSValidationError as e:
        print(f"✗ Validation failed: {e}")
        return

    # Demonstrate validation error handling
    print("\n--- Validation Error Demonstration ---")
    try:
        # Create an invalid document to show error handling
        invalid_product = ProductDetails(
            name="Invalid Product",
            product_id="invalid-001",
            visibility="public",
            status="production",
            type="dataset",
            language=["xyz"],  # Invalid ISO 639-1 code
            homepage="not-a-url",  # Invalid URI
        )
        invalid_odp = OpenDataProduct(invalid_product)
        invalid_odp.data_holder = DataHolder(
            name="Invalid Holder",
            email="not-an-email",  # Invalid email
            phone_number="123",  # Invalid phone
        )
        invalid_odp.validate()
    except ODPSValidationError as e:
        print("✓ Standards validation working correctly:")
        print(f"   {e}")

    # Convert to different formats
    print("\n--- JSON Output ---")
    json_output = odp.to_json()
    print(json_output[:500] + "..." if len(json_output) > 500 else json_output)

    print("\n--- YAML Output ---")
    yaml_output = odp.to_yaml()
    print(yaml_output[:500] + "..." if len(yaml_output) > 500 else yaml_output)

    # Save to files
    odp.save("weather-data-product.json")
    odp.save("weather-data-product.yaml")
    print("\n✓ Saved to weather-data-product.json and weather-data-product.yaml")

    # Load from file and verify
    print("\nLoading and verifying from file...")
    loaded_odp = OpenDataProduct.from_file("weather-data-product.json")
    loaded_odp.validate()  # Re-validate loaded document
    print(f"✓ Loaded and validated: {loaded_odp}")
    print(f"  Languages: {loaded_odp.product_details.language}")
    access_methods = 1 if loaded_odp.data_access else 0
    if loaded_odp.data_access and loaded_odp.data_access.additional_methods:
        access_methods += len(loaded_odp.data_access.additional_methods)
    print(f"  Data Access Methods: {access_methods}")
    print(
        f"  Pricing Plans: {len(loaded_odp.pricing_plans.plans) if loaded_odp.pricing_plans else 0}"
    )


if __name__ == "__main__":
    main()
