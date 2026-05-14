# Changelog

All notable changes to the ODPS Python library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - v4.1 Support

### 🎉 ODPS v4.1 Support

Updated to add support for ODPS v4.1 specification with ProductStrategy, AI agent integration, and enhanced referencing capabilities.

#### ✨ New Features (v4.1)

**ProductStrategy Component**
- Added `ProductStrategy` dataclass for connecting data products to business objectives
- Added `KPI` dataclass for defining Key Performance Indicators
- Support for business objectives, contributesToKPI, productKPIs, and relatedKPIs
- Strategic alignment tracking with corporate initiatives
- Added `KPIDirection` enum: increase, decrease, at_least, at_most, equals
- Added `KPIUnit` enum: percentage, minutes, seconds, count, currency, and more
- Comprehensive validation for ProductStrategy and KPI fields
- Added `ProductStrategyValidator` to validation framework

**AI Agent Integration**
- Added `AI` output port type for AI agent data access
- Support for Model Context Protocol (MCP) specification
- AI agent-native delivery mechanisms
- Autonomous machine consumption patterns

**Enhanced $ref Support**
- Added `dollar_ref` field to DataContract, SLA, DataQuality, DataAccess, and PaymentGateway models
- JSON Reference syntax support for internal references (#/product/...)
- JSON Reference syntax support for external URL-based references
- DRY principle implementation for component reusability

**Schema Updates**
- Updated schema URL to `https://opendataproducts.org/v4.1/schema/odps.json`
- Updated version to `4.1`
- Full backward compatibility with v4.0 documents

#### 🔧 Technical Improvements
- Added field mappings for ProductStrategy serialization (snake_case ↔ camelCase)
- Extended `OpenDataProduct.__slots__` with `product_strategy` field
- Updated `_generate_hash()` to include product_strategy for cache invalidation
- Enhanced `to_dict()` with ProductStrategy and nested KPI serialization
- Enhanced `from_dict()` with ProductStrategy and KPI parsing
- Updated all component docstrings to reference v4.1

#### 📚 Documentation
- Updated README.md with v4.1 feature overview
- Added comprehensive v4.1 example (examples/odps_v41_example.py)
- Updated Quick Start guide with ProductStrategy usage
- Updated Optional Components list with v4.1 additions
- Added links to v4.0 → v4.1 migration guide

#### 🔄 Migration Notes
- **Fully backward compatible** - v4.0 documents work without modification
- ProductStrategy is optional - existing code continues to function
- New KPI enums available but optional
- AI output port type is optional enhancement
- $ref support is optional feature

## [0.1.0] - 2024-08-19

### 🎉 Initial Release

A comprehensive Python library for creating, validating, and manipulating Open Data Product Specification (ODPS) v4.0 documents with full international standards compliance.

#### ✨ Core Features
- **Complete ODPS v4.0 Support**: Full implementation of the Open Data Product Specification v4.0
- **International Standards Compliance**: Built-in validation for ISO, RFC, and ITU-T standards
- **High Performance**: Optimized with caching, `__slots__`, and efficient validation patterns
- **Type Safety**: Comprehensive type hints, protocols, and runtime type checking
- **Modular Architecture**: Pluggable validators and extensible component system

#### 🌍 International Standards Validation
- **ISO 639-1**: Language code validation for multilingual fields
- **ISO 3166-1 alpha-2**: Country code validation
- **ISO 4217**: Currency code validation for pricing plans
- **ISO 8601**: Date/time format validation
- **E.164**: International phone number format validation
- **RFC 5322**: Email address validation
- **RFC 3986**: URI/URL validation for all link fields

#### 🏗️ Architecture & Design
- **Protocol-Based Architecture**: Type-safe interfaces using Python protocols
- **Validation Framework**: Modular, pluggable validation system
- **Exception Hierarchy**: Comprehensive error handling with 20+ specialized exceptions
- **Performance Optimizations**: Caching system with hash-based invalidation
- **Memory Efficiency**: `__slots__` implementation across all models

#### 📦 Components Supported
- **ProductDetails**: Core product information with all ODPS v4.0 attributes
- **DataAccess**: Data access methods with required default method enforcement
- **DataHolder**: Complete contact and organizational information
- **License**: Comprehensive licensing terms and conditions
- **PricingPlans**: Flexible pricing with multi-currency support
- **DataContract**: Contract specifications with ODCS/DCS support
- **SLA & DataQuality**: Service level and quality profiles
- **PaymentGateway**: Payment processing integration
- **SpecificationExtensions**: Custom `x-` prefixed fields support

#### 🔧 Technical Features
- **Smart Properties**: `is_valid`, `validation_errors`, `compliance_level`
- **Serialization**: JSON/YAML export with proper camelCase conversion
- **File I/O**: Load/save from files with automatic format detection
- **Multilingual Support**: Full support for multilingual dictionaries
- **Caching System**: Up to 45x performance improvement on repeated operations

#### 🧪 Quality & Testing
- Comprehensive test suite with >90% coverage
- Protocol compliance testing
- Performance benchmarking
- International standards validation testing
- Example scripts and documentation

#### 📖 Documentation & Examples
- Complete API documentation with docstrings
- Basic usage examples in `examples/basic_usage.py`
- Advanced features demo in `examples/advanced_features.py`
- Comprehensive example in `examples/comprehensive_example.py`
- Demo ODPS documents in JSON and YAML formats

#### 📋 Dependencies
- **Core**: `PyYAML>=6.0.2`
- **Standards Validation**: `pycountry>=24.6.1`, `phonenumbers>=9.0.11`
- **Development**: Full development toolkit with testing, linting, and type checking

#### 🚀 Getting Started
```python
from open_data_products.odps import OpenDataProduct, ProductDetails

# Create a new ODPS document
product = ProductDetails(
    name="My Data Product",
    product_id="my-product-001",
    visibility="public",
    status="production",
    type="dataset"
)

odp = OpenDataProduct(product)
odp.validate()  # Full standards compliance validation
print(odp.to_json())  # Export to JSON
```

---

*For complete documentation and examples, see the [README](README.md) and [examples/](examples/) directory.*