# Open Data Products Python SDK

[![PyPI version](https://badge.fury.io/py/odps-python.svg)](https://badge.fury.io/py/odps-python)
[![Python Support](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://github.com/accenture/odps-python)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A comprehensive, high-performance Python library for creating, validating, and manipulating [Open Data Product Specification (ODPS) v4.1](https://opendataproducts.org/v4.1/) documents with full international standards compliance.

## 🚀 Features

### ODPS v4.1 Features (NEW!)
- **ProductStrategy**: Connect data products to business objectives, KPIs, and strategic initiatives
- **KPI Support**: Define and track Key Performance Indicators with targets, units, and calculations
- **AI Agent Integration**: Support for AI agents via Model Context Protocol (MCP)
- **Enhanced $ref Support**: JSON Reference syntax for component reusability

### Core Capabilities
- **Complete ODPS v4.1 Support**: Full implementation of the latest Open Data Product Specification
- **International Standards Compliance**: Validates against ISO, RFC, and ITU-T standards
- **Flexible I/O**: JSON and YAML serialization/deserialization support
- **Type Safety**: Comprehensive type hints and protocol-based duck typing
- **Multilingual Support**: Full support for multilingual field dictionaries

### Performance & Architecture
- **High Performance**: Optimized with validation caching, serialization caching, and `__slots__`
- **Modular Architecture**: Pluggable validation framework and component system
- **Protocol-Based Design**: Duck typing protocols for better type safety
- **Comprehensive Error Handling**: Hierarchical exception system with 20+ specific error types

### Standards Validation
- **ISO 639-1**: Language code validation
- **ISO 3166-1 alpha-2**: Country code validation
- **ISO 4217**: Currency code validation
- **ISO 8601**: Date/time format validation
- **ITU-T E.164**: Phone number format validation
- **RFC 5322**: Email address validation
- **RFC 3986**: URI/URL validation

### Developer Experience
- **Comprehensive Documentation**: Full API documentation and examples
- **IDE Support**: Complete type hints for excellent IntelliSense
- **Detailed Error Messages**: Specific validation errors with context

## Installation

```bash
pip install open-data-products

# For full standards validation support:
pip install "open-data-products[validation]"

# For development:
pip install "open-data-products[dev]"
```

Existing ODPS users can continue importing from `odps` during the compatibility period. New code should prefer `open_data_products.odps` because the SDK is expanding to support the broader OpenDataProducts.org standards family.

## Quick Start

### Basic Usage (v4.1)

```python
from open_data_products.odps import OpenDataProduct
from open_data_products.odps.models import (
    ProductDetails,
    ProductStrategy,
    KPI,
    DataAccessMethod,
    DataHolder,
    License
)

# Create a new data product with international standards compliance
product = ProductDetails(
    name="My Weather API",
    product_id="weather-api-v1",
    visibility="public",
    status="production",
    type="dataset",
    description="Real-time weather data",
    language=["en", "fr"],  # ISO 639-1 language codes
    homepage="https://example.com"  # RFC 3986 compliant URI
)

# Create ODPS document
odp = OpenDataProduct(product)

# NEW in v4.1: Add ProductStrategy to connect to business objectives
strategy = ProductStrategy(
    objectives=["Improve weather forecasting accuracy for disaster prevention"],
    contributes_to_kpi=KPI(
        name="Disaster Prevention Response Time",
        unit="minutes",
        target=15,
        direction="at_most",
        calculation="Time from alert to action"
    ),
    product_kpis=[
        KPI(
            name="Forecast Accuracy",
            unit="percentage",
            target=95,
            direction="at_least"
        )
    ]
)
odp.product_strategy = strategy

# Add data access with required default method
default_access = DataAccessMethod(
    name={"en": "REST API", "fr": "API REST"},  # Multilingual support
    output_port_type="API",
    access_url="https://api.example.com/weather",  # RFC 3986 URI
    documentation_url="https://docs.example.com"   # RFC 3986 URI
)
odp.add_data_access(default_access)

# Add data holder with validated contact info
odp.data_holder = DataHolder(
    name="Weather Corp",
    email="contact@example.com",  # RFC 5322 email validation
    phone_number="+12125551234"    # E.164 phone validation
)

# Add license with ISO 8601 date validation
odp.license = License(
    scope_of_use="commercial",
    valid_from="2024-01-01",          # ISO 8601 date
    valid_until="2025-12-31T23:59:59Z"  # ISO 8601 datetime
)

# Comprehensive validation with all standards
try:
    odp.validate()
    print("✓ Document valid with full standards compliance")
except Exception as e:
    print(f"Validation errors: {e}")

# Export
print(odp.to_json())
odp.save("my-product.json")

# Load existing document
loaded = OpenDataProduct.from_file("my-product.json")
```

## Core Components

### ProductDetails (Required)
- `name`: Product name
- `product_id`: Unique identifier  
- `visibility`: public, private, etc.
- `status`: draft, production, etc.
- `type`: dataset, algorithm, etc.

### Optional Components
- **ProductStrategy** (NEW v4.1): Business objectives, KPIs, and strategic alignment
- **DataContract**: API specifications and data schemas (now with $ref support)
- **SLA**: Service level agreements (now with $ref support)
- **DataQuality**: Quality metrics and rules (now with $ref support)
- **PricingPlans**: Pricing tiers with ISO 4217 currency validation
- **License**: Usage rights with ISO 8601 date validation
- **DataAccess**: Access methods including AI agent support (NEW v4.1: MCP protocol)
- **DataHolder**: Contact information with email/phone validation
- **PaymentGateways**: Payment processing details (now with $ref support)

## Validation Standards

The library enforces all international standards referenced in ODPS v4.1:

| Standard | Used For | Example |
|----------|----------|----------|
| **ISO 639-1** | Language codes | `"en"`, `"fr"`, `"de"` |
| **ISO 3166-1 alpha-2** | Country codes | `"US"`, `"GB"`, `"DE"` |
| **ISO 4217** | Currency codes | `"USD"`, `"EUR"`, `"GBP"` |
| **ISO 8601** | Date/time formats | `"2024-01-01"`, `"2024-01-01T12:00:00Z"` |
| **E.164** | Phone numbers | `"+12125551234"` |
| **RFC 5322** | Email addresses | `"user@example.com"` |
| **RFC 3986** | URIs/URLs | `"https://example.com/api"` |

### Multilingual Support

Fields like `dataAccess.name` and `dataAccess.description` support multilingual dictionaries:

```python
{
    "name": {
        "en": "Weather API",
        "fr": "API Météo",
        "de": "Wetter-API"
    }
}
```

All language keys are validated against ISO 639-1 standards.

## ⚡ Performance Features

### Intelligent Caching
The library includes sophisticated caching for optimal performance:

```python
import time
from odps import OpenDataProduct, ProductDetails

# Create a product
details = ProductDetails(
    name="Performance Test",
    product_id="perf-001", 
    visibility="public",
    status="draft",
    type="dataset"
)
product = OpenDataProduct(details)

# First validation - full processing
start = time.time()
product.validate()
first_time = time.time() - start

# Second validation - cached result
start = time.time()
product.validate()
cached_time = time.time() - start

print(f"Cache speedup: {first_time/cached_time:.1f}x")  # Typically 20-50x faster
```

### Compliance Assessment
```python
# Comprehensive compliance checking
compliance_level = product.compliance_level  # "minimal", "basic", "substantial", "full"
is_production_ready = product.is_production_ready
validation_errors = product.validation_errors  # No exceptions raised
component_count = product.component_count
```

## 🔧 Advanced Usage

### Custom Validation

```python
from odps.validators import ODPSValidator

# Validate individual components
print(ODPSValidator.validate_iso639_language_code("en"))  # True
print(ODPSValidator.validate_currency_code("USD"))        # True
print(ODPSValidator.validate_email("test@example.com"))   # True
print(ODPSValidator.validate_phone_number("+12125551234"))  # True
print(ODPSValidator.validate_iso8601_date("2024-01-01"))    # True
```

### Loading from Different Formats

```python
# From JSON
odp = OpenDataProduct.from_json(json_string)

# From YAML  
odp = OpenDataProduct.from_yaml(yaml_string)

# From file (auto-detects format)
odp = OpenDataProduct.from_file("product.json")
odp = OpenDataProduct.from_file("product.yaml")
```

## Development

```bash
git clone https://github.com/accenture/odps-python
cd odps-python
pip install -e ".[dev]"
python examples/comprehensive_example.py
```

### Dependencies

The library requires the following packages for full standards compliance:
- `pycountry`: ISO standards validation (languages, countries, currencies)
- `phonenumbers`: E.164 phone number validation
- `PyYAML`: YAML format support

## License

Apache License 2.0 - see LICENSE file for details.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## Error Handling

The library provides detailed validation error messages that reference specific standards:

```python
try:
    odp.validate()
except ODPSValidationError as e:
    print(e)
    # Output: "Validation errors: Invalid ISO 639-1 language code: 'xyz'; 
    #          dataHolder email must be a valid RFC 5322 email address"
```

## 📖 Examples

### Complete v4.1 Example
See [examples/odps_v41_example.py](examples/odps_v41_example.py) for a comprehensive demonstration of all v4.1 features including:
- ProductStrategy with business objectives
- KPI definitions with targets and calculations
- AI agent integration via MCP
- Enhanced $ref support

Run the example:
```bash
python examples/odps_v41_example.py
```

### Additional Examples
- [Basic ODPS Creation](examples/basic_example.py)
- [Comprehensive ODPS Document](examples/comprehensive_example.py)
- [Validation Examples](examples/validation_example.py)

## 🏆 Acknowledgments

We extend our gratitude to the following:

**[Open Data Product Initiative Team](https://opendataproducts.org/)** - Special thanks to the team at opendataproducts.org for their work in creating and maintaining the Open Data Product Specification (ODPS). Their vision of standardizing data product descriptions and enabling better data discovery and interoperability has made this library possible. The ODPS v4.1 specification represents years of collaborative effort from industry experts, data practitioners, and open source contributors who are driving the future of data standardization.

**Python Community** - For the exceptional ecosystem of libraries and tools that power this implementation, including PyYAML, pycountry, phonenumbers, and the countless other packages that make Python development a joy.

**Data Community** - For embracing open standards and driving the need for better data product specifications and tooling that benefits everyone in the data ecosystem.

**Documentation Support** - Documentation assistance provided by Claude (Anthropic).

## 📚 Links & References

- [Open Data Product Specification v4.1](https://opendataproducts.org/v4.1/)
- [ODPS v4.0 → v4.1 Migration Guide](https://opendataproducts.org/v4.1/#odps-4-0-4-1-migration-guide)
- [ODPS Schema](https://opendataproducts.org/v4.1/schema/)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [ISO 3166-1 Country Codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
- [ISO 4217 Currency Codes](https://en.wikipedia.org/wiki/ISO_4217)
- [ISO 8601 Date/Time Format](https://en.wikipedia.org/wiki/ISO_8601)
- [E.164 Phone Number Format](https://en.wikipedia.org/wiki/E.164)
- [RFC 5322 Email Format](https://datatracker.ietf.org/doc/html/rfc5322)
- [RFC 3986 URI Format](https://datatracker.ietf.org/doc/html/rfc3986)
