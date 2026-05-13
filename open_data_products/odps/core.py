# Copyright 2024 ODPS Python Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Core OpenDataProduct class for handling ODPS documents.

This module provides the main OpenDataProduct class that implements the Open Data Product
Specification (ODPS) v4.0. It supports creating, loading, validating, and manipulating
ODPS documents with full element compliance to appropriate international standards.

Key Features:
    - Full ODPS v4.0 specification compliance
    - JSON and YAML serialization/deserialization
    - Comprehensive validation with detailed error reporting
    - Performance optimizations with caching and __slots__
    - Protocol-based duck typing for better type safety
    - Modular component architecture

Example:
    Basic usage of OpenDataProduct:

    >>> from odps import OpenDataProduct, ProductDetails
    >>> details = ProductDetails(
    ...     name="My Data Product",
    ...     product_id="dp-001",
    ...     visibility="public",
    ...     status="draft",
    ...     type="dataset"
    ... )
    >>> product = OpenDataProduct(details)
    >>> product.validate()
    True
    >>> json_output = product.to_json()

Classes:
    OpenDataProduct: Main class for handling ODPS documents

See Also:
    - models.py: Data model classes for ODPS components
    - validation.py: Validation framework and rules
    - protocols.py: Type protocols for duck typing
"""

import json
import yaml
from dataclasses import asdict
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import hashlib

from .models import (
    ProductDetails,
    ProductStrategy,
    KPI,
    DataContract,
    SLA,
    DataQuality,
    PricingPlans,
    License,
    DataAccess,
    DataAccessMethod,
    DataHolder,
    PaymentGateways,
    UseCase,
    SpecificationExtensions,
)
from .validation import ODPSValidationFramework
from .exceptions import (
    ODPSValidationError,
    ODPSJSONParsingError,
    ODPSYAMLParsingError,
    ODPSFileNotFoundError,
)
from .protocols import is_validatable, validate_protocol_compliance

class OpenDataProduct:
    """
    Main class for handling Open Data Product Specification (ODPS) v4.0 documents.

    This class provides comprehensive support for creating, loading, validating, and
    manipulating ODPS documents. It implements the full ODPS v4.0 specification with
    performance optimizations and type safety.

    The class supports all ODPS components including:
    - Product Details (required)
    - Data Contract (optional)
    - Service Level Agreement (SLA) (optional)
    - Data Quality specifications (optional)
    - Pricing Plans (optional)
    - License information (optional)
    - Data Access methods (optional)
    - Data Holder information (optional)
    - Payment Gateways (optional)
    - Custom Extensions (optional)

    Attributes:
        schema (str): ODPS schema URL (https://opendataproducts.org/v4.0/schema/odps.json)
        version (str): ODPS version (4.0)
        product_details (ProductDetails): Core product information (required)
        data_contract (DataContract, optional): Data contract specifications
        sla (SLA, optional): Service level agreement
        data_quality (DataQuality, optional): Data quality specifications
        pricing_plans (PricingPlans, optional): Pricing information
        license (License, optional): License terms and conditions
        data_access (DataAccess, optional): Data access methods and endpoints
        data_holder (DataHolder, optional): Data holder/provider information
        payment_gateways (PaymentGateways, optional): Payment processing information
        extensions (SpecificationExtensions, optional): Custom extension fields

    Performance Features:
        - Validation result caching for repeated validation calls
        - Serialization caching for JSON/YAML output
        - __slots__ for memory efficiency
        - Automatic cache invalidation when object state changes

    Example:
        Creating a basic ODPS document:

        >>> from odps import OpenDataProduct, ProductDetails
        >>> details = ProductDetails(
        ...     name="Customer Demographics Dataset",
        ...     product_id="cust-demo-001",
        ...     visibility="public",
        ...     status="production",
        ...     type="dataset",
        ...     description="Anonymized customer demographic data"
        ... )
        >>> product = OpenDataProduct(details)
        >>>
        >>> # Add optional components
        >>> from odps.models import License
        >>> product.add_license(
        ...     scope_of_use="commercial",
        ...     geographical_area=["US", "EU"]
        ... )
        >>>
        >>> # Validate and export
        >>> is_valid = product.validate()  # True
        >>> json_str = product.to_json()
        >>> product.save("my_data_product.json")

        Loading from existing document:

        >>> product = OpenDataProduct.from_file("existing_product.json")
        >>> compliance_level = product.compliance_level  # "full", "substantial", etc.
        >>> has_license = product.license is not None

    Note:
        All appropriate element validation follows international standards including:
        - ISO 639-1 (language codes)
        - ISO 3166-1 (country codes)
        - ISO 4217 (currency codes)
        - ISO 8601 (date/time formats)
        - RFC 5322 (email addresses)
        - RFC 3986 (URIs)
        - ITU-T E.164 (phone numbers)
    """

    __slots__ = [
        "schema",
        "version",
        "product_details",
        "product_strategy",
        "data_contract",
        "sla",
        "data_quality",
        "pricing_plans",
        "license",
        "data_access",
        "data_holder",
        "payment_gateways",
        "extensions",
        "_validation_cache",
        "_serialization_cache",
        "_hash_cache",
    ]

    REQUIRED_SCHEMA = "https://opendataproducts.org/v4.1/schema/odps.json"
    REQUIRED_VERSION = "4.1"

    # Field mapping for snake_case to camelCase conversion
    PRODUCT_DETAILS_MAPPING = {
        "product_id": "productID",
        "value_proposition": "valueProposition",
        "logo_url": "logoURL",
        "product_series": "productSeries",
        "product_version": "productVersion",
        "version_notes": "versionNotes",
        "content_sample": "contentSample",
        "brand_slogan": "brandSlogan",
        "use_cases": "useCases",
        "recommended_data_products": "recommendedDataProducts",
        "output_file_formats": "outputFileFormats",
    }

    DATA_CONTRACT_MAPPING = {
        "contract_version": "contractVersion",
        "contract_url": "contractURL",
        "dollar_ref": "$ref",
    }

    PRODUCT_STRATEGY_MAPPING = {
        "contributes_to_kpi": "contributesToKPI",
        "product_kpis": "productKPIs",
        "related_kpis": "relatedKPIs",
        "strategic_alignment": "strategicAlignment",
    }

    KPI_MAPPING = {
        # All KPI fields use their existing names (no camelCase conversion needed)
    }

    LICENSE_MAPPING = {
        "scope_of_use": "scopeOfUse",
        "geographical_area": "geographicalArea",
        "right_to_sublicense": "rightToSublicense",
        "right_to_modify": "rightToModify",
        "valid_from": "validFrom",
        "valid_until": "validUntil",
        "license_grant": "licenseGrant",
        "license_name": "licenseName",
        "license_url": "licenseURL",
        "scope_details": "scopeDetails",
        "termination_conditions": "terminationConditions",
        "governance_specifics": "governanceSpecifics",
        "audit_terms": "auditTerms",
        "confidentiality_clauses": "confidentialityClauses",
    }

    DATA_HOLDER_MAPPING = {
        "phone_number": "phoneNumber",
        "business_identifiers": "businessIdentifiers",
        "contact_person": "contactPerson",
        "contact_phone": "contactPhone",
        "contact_email": "contactEmail",
        "address_street": "addressStreet",
        "address_city": "addressCity",
        "address_state": "addressState",
        "address_postal_code": "addressPostalCode",
        "address_country": "addressCountry",
        "organizational_description": "organizationalDescription",
    }

    PRICING_PLAN_MAPPING = {
        "price_currency": "priceCurrency",
        "billing_duration": "billingDuration",
        "max_transactions_per_second": "maxTransactionsPerSecond",
        "max_transactions_per_month": "maxTransactionsPerMonth",
        "min_price": "minPrice",
        "max_price": "maxPrice",
        "value_added_tax": "valueAddedTax",
        "valid_from": "validFrom",
        "valid_to": "validTo",
        "additional_pricing_details": "additionalPricingDetails",
        "quality_profile_reference": "qualityProfileReference",
        "sla_profile_reference": "slaProfileReference",
        "access_profile_reference": "accessProfileReference",
    }

    DATA_ACCESS_MAPPING = {
        "output_port_type": "outputPorttype",
        "access_url": "accessURL",
        "authentication_method": "authenticationMethod",
        "specs_url": "specsURL",
        "documentation_url": "documentationURL",
        "dollar_ref": "$ref",
    }

    PAYMENT_GATEWAY_MAPPING = {
        "executable_specifications": "executableSpecifications",
        "dollar_ref": "$ref",
    }

    SLA_MAPPING = {
        "dollar_ref": "$ref",
    }

    DATA_QUALITY_MAPPING = {
        "dollar_ref": "$ref",
    }

    @staticmethod
    def _convert_snake_to_camel(
        data_dict: Dict[str, Any], mapping: Dict[str, str]
    ) -> None:
        """
        Convert snake_case keys to camelCase using provided mapping.

        Args:
            data_dict: Dictionary to modify in-place
            mapping: Dictionary mapping snake_case keys to camelCase keys
        """
        for snake_key, camel_key in mapping.items():
            if snake_key in data_dict:
                data_dict[camel_key] = data_dict.pop(snake_key)

    def _generate_hash(self) -> str:
        """Generate hash of current object state for cache invalidation."""
        if self._hash_cache is None:
            # Create a simple hash based on key object properties
            state_data = {
                "schema": self.schema,
                "version": self.version,
                "product_details": str(self.product_details),
                "product_strategy": str(self.product_strategy),
                "data_contract": str(self.data_contract),
                "sla": str(self.sla),
                "data_quality": str(self.data_quality),
                "pricing_plans": str(self.pricing_plans),
                "license": str(self.license),
                "data_access": str(self.data_access),
                "data_holder": str(self.data_holder),
                "payment_gateways": str(self.payment_gateways),
                "extensions": str(self.extensions),
            }
            state_str = json.dumps(state_data, sort_keys=True)
            self._hash_cache = hashlib.md5(state_str.encode(), usedforsecurity=False).hexdigest()

        return self._hash_cache

    def _invalidate_cache(self) -> None:
        """Invalidate all caches when object state changes."""
        self._validation_cache.clear()
        self._serialization_cache.clear()
        self._hash_cache = None

    def __init__(self, product_details: ProductDetails):
        """
        Initialize with mandatory product details

        Args:
            product_details: ProductDetails instance with core product info
        """
        self.schema = self.REQUIRED_SCHEMA
        self.version = self.REQUIRED_VERSION
        self.product_details = product_details

        # Optional components
        self.product_strategy: Optional[ProductStrategy] = None  # New in v4.1
        self.data_contract: Optional[DataContract] = None
        self.sla: Optional[SLA] = None
        self.data_quality: Optional[DataQuality] = None
        self.pricing_plans: Optional[PricingPlans] = None
        self.license: Optional[License] = None
        self.data_access: Optional[DataAccess] = None
        self.data_holder: Optional[DataHolder] = None
        self.payment_gateways: Optional[PaymentGateways] = None
        self.extensions: Optional[SpecificationExtensions] = None

        # Performance caches
        self._validation_cache: Dict[str, Any] = {}
        self._serialization_cache: Dict[str, str] = {}
        self._hash_cache: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenDataProduct":
        """
        Create OpenDataProduct from dictionary

        Args:
            data: Dictionary containing ODPS document data

        Returns:
            OpenDataProduct instance
        """
        # Extract and validate core fields
        schema = data.get("schema")
        version = data.get("version")
        product_data = data.get("product", {})

        if not product_data:
            raise ODPSValidationError("Missing required 'product' section")

        # Parse use cases
        use_cases = []
        for uc_data in product_data.get("useCases", []):
            use_case = UseCase(
                title=uc_data.get("title", ""),
                description=uc_data.get("description", ""),
                url=uc_data.get("url"),
            )
            use_cases.append(use_case)

        # Create ProductDetails with all optional attributes
        product_details = ProductDetails(
            name=product_data.get("name", ""),
            product_id=product_data.get("productID", ""),
            visibility=product_data.get("visibility", ""),
            status=product_data.get("status", ""),
            type=product_data.get("type", ""),
            value_proposition=product_data.get("valueProposition"),
            description=product_data.get("description"),
            categories=product_data.get("categories", []),
            tags=product_data.get("tags", []),
            brand=product_data.get("brand"),
            keywords=product_data.get("keywords", []),
            themes=product_data.get("themes", []),
            geography=product_data.get("geography"),
            language=product_data.get("language", []),
            homepage=product_data.get("homepage"),
            logo_url=product_data.get("logoURL"),
            # Additional optional attributes
            created=product_data.get("created"),
            updated=product_data.get("updated"),
            product_series=product_data.get("productSeries"),
            standards=product_data.get("standards", []),
            product_version=product_data.get("productVersion"),
            version_notes=product_data.get("versionNotes"),
            issues=product_data.get("issues"),
            content_sample=product_data.get("contentSample"),
            brand_slogan=product_data.get("brandSlogan"),
            use_cases=use_cases,
            recommended_data_products=product_data.get("recommendedDataProducts", []),
            output_file_formats=product_data.get("outputFileFormats", []),
        )

        instance = cls(product_details)
        instance.schema = schema or cls.REQUIRED_SCHEMA
        instance.version = version or cls.REQUIRED_VERSION

        # Load product strategy (v4.1)
        if "productStrategy" in product_data:
            ps_data = product_data["productStrategy"]

            # Parse contributes_to_kpi
            contributes_to_kpi = None
            if "contributesToKPI" in ps_data:
                kpi_data = ps_data["contributesToKPI"]
                contributes_to_kpi = KPI(
                    name=kpi_data.get("name", ""),
                    id=kpi_data.get("id"),
                    description=kpi_data.get("description"),
                    unit=kpi_data.get("unit"),
                    target=kpi_data.get("target"),
                    direction=kpi_data.get("direction"),
                    timeframe=kpi_data.get("timeframe"),
                    frequency=kpi_data.get("frequency"),
                    owner=kpi_data.get("owner"),
                    calculation=kpi_data.get("calculation"),
                )

            # Parse product_kpis
            product_kpis = []
            for kpi_data in ps_data.get("productKPIs", []):
                kpi = KPI(
                    name=kpi_data.get("name", ""),
                    id=kpi_data.get("id"),
                    description=kpi_data.get("description"),
                    unit=kpi_data.get("unit"),
                    target=kpi_data.get("target"),
                    direction=kpi_data.get("direction"),
                    timeframe=kpi_data.get("timeframe"),
                    frequency=kpi_data.get("frequency"),
                    owner=kpi_data.get("owner"),
                    calculation=kpi_data.get("calculation"),
                )
                product_kpis.append(kpi)

            # Parse related_kpis
            related_kpis = []
            for kpi_data in ps_data.get("relatedKPIs", []):
                kpi = KPI(
                    name=kpi_data.get("name", ""),
                    id=kpi_data.get("id"),
                    description=kpi_data.get("description"),
                    unit=kpi_data.get("unit"),
                    target=kpi_data.get("target"),
                    direction=kpi_data.get("direction"),
                    timeframe=kpi_data.get("timeframe"),
                    frequency=kpi_data.get("frequency"),
                    owner=kpi_data.get("owner"),
                    calculation=kpi_data.get("calculation"),
                )
                related_kpis.append(kpi)

            instance.product_strategy = ProductStrategy(
                objectives=ps_data.get("objectives", []),
                contributes_to_kpi=contributes_to_kpi,
                product_kpis=product_kpis,
                related_kpis=related_kpis,
                strategic_alignment=ps_data.get("strategicAlignment", []),
            )

        # Load data holder
        if "dataHolder" in product_data:
            dh_data = product_data["dataHolder"]
            instance.data_holder = DataHolder(
                name=dh_data.get("name", ""),
                email=dh_data.get("email", ""),
                url=dh_data.get("url"),
                phone_number=dh_data.get("phoneNumber"),
                address=dh_data.get("address"),
                # Additional optional attributes
                business_identifiers=dh_data.get("businessIdentifiers", []),
                contact_person=dh_data.get("contactPerson"),
                contact_phone=dh_data.get("contactPhone"),
                contact_email=dh_data.get("contactEmail"),
                address_street=dh_data.get("addressStreet"),
                address_city=dh_data.get("addressCity"),
                address_state=dh_data.get("addressState"),
                address_postal_code=dh_data.get("addressPostalCode"),
                address_country=dh_data.get("addressCountry"),
                ratings=dh_data.get("ratings"),
                organizational_description=dh_data.get("organizationalDescription"),
            )

        # Load pricing plans
        if "pricingPlans" in product_data:
            pp_data = product_data["pricingPlans"]
            plans = []
            for plan_data in pp_data.get("plans", []):
                from .models import PricingPlan

                plan = PricingPlan(
                    name=plan_data.get("name", ""),
                    price_currency=plan_data.get("priceCurrency", ""),
                    price=plan_data.get("price"),
                    billing_duration=plan_data.get("billingDuration"),
                    unit=plan_data.get("unit"),
                    max_transactions_per_second=plan_data.get(
                        "maxTransactionsPerSecond"
                    ),
                    max_transactions_per_month=plan_data.get("maxTransactionsPerMonth"),
                )
                plans.append(plan)
            instance.pricing_plans = PricingPlans(plans=plans)

        # Load optional components
        if "dataContract" in product_data:
            dc_data = product_data["dataContract"]
            instance.data_contract = DataContract(
                id=dc_data.get("id"),
                type=dc_data.get("type"),
                contract_version=dc_data.get("contractVersion"),
                contract_url=dc_data.get("contractURL"),
                spec=dc_data.get("spec"),
                ref=dc_data.get("ref"),
                dollar_ref=dc_data.get("$ref"),
            )

        if "SLA" in product_data:
            # TODO: Parse SLA profiles from data
            instance.sla = SLA()

        if "dataQuality" in product_data:
            # TODO: Parse DataQuality profiles from data
            instance.data_quality = DataQuality()

        if "dataAccess" in product_data:
            da_data = product_data["dataAccess"]
            if "default" not in da_data:
                raise ODPSValidationError("dataAccess requires a 'default' method")

            default_method = DataAccessMethod(
                name=da_data["default"].get("name"),
                description=da_data["default"].get("description"),
                output_port_type=da_data["default"].get("outputPorttype"),
                format=da_data["default"].get("format"),
                access_url=da_data["default"].get("accessURL"),
                authentication_method=da_data["default"].get("authenticationMethod"),
                specs_url=da_data["default"].get("specsURL"),
                documentation_url=da_data["default"].get("documentationURL"),
                specification=da_data["default"].get("specification"),
            )

            additional_methods = {}
            for key, method_data in da_data.items():
                if key != "default":
                    additional_methods[key] = DataAccessMethod(
                        name=method_data.get("name"),
                        description=method_data.get("description"),
                        output_port_type=method_data.get("outputPorttype"),
                        format=method_data.get("format"),
                        access_url=method_data.get("accessURL"),
                        authentication_method=method_data.get("authenticationMethod"),
                        specs_url=method_data.get("specsURL"),
                        documentation_url=method_data.get("documentationURL"),
                        specification=method_data.get("specification"),
                    )

            instance.data_access = DataAccess(
                default=default_method, additional_methods=additional_methods
            )

        if "license" in product_data:
            license_data = product_data["license"]
            instance.license = License(
                scope_of_use=license_data.get("scopeOfUse", ""),
                geographical_area=license_data.get("geographicalArea", []),
                permanent=license_data.get("permanent", True),
                exclusive=license_data.get("exclusive", False),
                right_to_sublicense=license_data.get("rightToSublicense", False),
                right_to_modify=license_data.get("rightToModify", False),
                valid_from=license_data.get("validFrom"),
                valid_until=license_data.get("validUntil"),
                license_grant=license_data.get("licenseGrant"),
                license_name=license_data.get("licenseName"),
                license_url=license_data.get("licenseURL"),
                # Additional optional attributes
                scope_details=license_data.get("scopeDetails"),
                termination_conditions=license_data.get("terminationConditions"),
                governance_specifics=license_data.get("governanceSpecifics"),
                audit_terms=license_data.get("auditTerms"),
                warranties=license_data.get("warranties"),
                damages=license_data.get("damages"),
                confidentiality_clauses=license_data.get("confidentialityClauses"),
            )

        # Load extensions (x- prefixed fields)
        extensions = SpecificationExtensions()
        for key, value in product_data.items():
            if key.startswith("x-"):
                extensions.add_extension(key, value)

        if extensions.extensions:
            instance.extensions = extensions

        return instance

    @classmethod
    def from_json(cls, json_str: str) -> "OpenDataProduct":
        """Load from JSON string"""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ODPSJSONParsingError(str(e))

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "OpenDataProduct":
        """Load from YAML string"""
        try:
            data = yaml.safe_load(yaml_str)
            return cls.from_dict(data)
        except yaml.YAMLError as e:
            raise ODPSYAMLParsingError(str(e))

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "OpenDataProduct":
        """Load from file (JSON or YAML)"""
        path = Path(file_path)

        if not path.exists():
            raise ODPSFileNotFoundError(str(file_path))

        content = path.read_text(encoding="utf-8")

        if path.suffix.lower() in [".json"]:
            return cls.from_json(content)
        elif path.suffix.lower() in [".yaml", ".yml"]:
            return cls.from_yaml(content)
        else:
            # Try JSON first, then YAML
            try:
                return cls.from_json(content)
            except (ODPSJSONParsingError, ODPSValidationError):
                return cls.from_yaml(content)

    def validate(self) -> bool:
        """
        Validate the ODPS document using the validation framework

        Returns:
            True if valid

        Raises:
            ODPSValidationError: If validation fails
        """
        # Check cache first
        current_hash = self._generate_hash()
        if current_hash in self._validation_cache:
            cached_result = self._validation_cache[current_hash]
            if cached_result.get("errors"):
                raise ODPSValidationError(cached_result["errors"])
            return cached_result.get("valid", False)

        # First check protocol compliance
        protocol_errors = validate_protocol_compliance(self, "ODPSDocumentProtocol")
        if protocol_errors:
            error_msg = f"Protocol compliance errors: {'; '.join(protocol_errors)}"
            self._validation_cache[current_hash] = {"valid": False, "errors": error_msg}
            raise ODPSValidationError(error_msg)

        # Then run standard validation
        validator = ODPSValidationFramework()
        errors = validator.validate(self)

        if errors:
            error_msg = f"Validation errors: {'; '.join(errors)}"
            self._validation_cache[current_hash] = {"valid": False, "errors": error_msg}
            raise ODPSValidationError(error_msg)

        # Cache successful validation
        self._validation_cache[current_hash] = {"valid": True, "errors": None}
        return True

    @property
    def is_valid(self) -> bool:
        """Check if document is valid without raising exceptions."""
        try:
            self.validate()
            return True
        except ODPSValidationError:
            return False

    @property
    def validation_errors(self) -> List[str]:
        """Get list of validation errors without raising exceptions."""
        try:
            self.validate()
            return []
        except ODPSValidationError as e:
            # Extract error messages from the exception string
            error_msg = str(e)
            if ": " in error_msg:
                errors_part = error_msg.split(": ", 1)[1]
                return errors_part.split("; ")
            return [error_msg]

    @property
    def has_optional_components(self) -> bool:
        """Check if document has any optional components."""
        return any(
            [
                self.data_contract is not None,
                self.sla is not None,
                self.data_quality is not None,
                self.pricing_plans is not None,
                self.license is not None,
                self.data_access is not None,
                self.data_holder is not None,
                self.payment_gateways is not None,
                self.extensions is not None,
            ]
        )

    @property
    def component_count(self) -> int:
        """Count of non-None optional components."""
        components = [
            self.data_contract,
            self.sla,
            self.data_quality,
            self.pricing_plans,
            self.license,
            self.data_access,
            self.data_holder,
            self.payment_gateways,
            self.extensions,
        ]
        return sum(1 for component in components if component is not None)

    @property
    def is_production_ready(self) -> bool:
        """Check if document is ready for production (valid + has required components)."""
        if not self.is_valid:
            return False

        # Production-ready typically means having at least data access
        return self.data_access is not None

    @property
    def compliance_level(self) -> str:
        """Get compliance level based on components present."""
        if not self.is_valid:
            return "invalid"

        required_for_full = {
            "data_access": self.data_access is not None,
            "license": self.license is not None,
            "data_holder": self.data_holder is not None,
        }

        present_count = sum(required_for_full.values())

        if present_count == 3:
            return "full"
        elif present_count >= 2:
            return "substantial"
        elif present_count >= 1:
            return "basic"
        else:
            return "minimal"

    def check_component_protocols(self) -> Dict[str, bool]:
        """Check if all components follow their respective protocols."""
        results = {
            "product_details": (
                is_validatable(self.product_details)
                if hasattr(self.product_details, "validate")
                else True
            ),
            "data_contract": (
                is_validatable(self.data_contract)
                if self.data_contract and hasattr(self.data_contract, "validate")
                else True
            ),
            "sla": (
                is_validatable(self.sla)
                if self.sla and hasattr(self.sla, "validate")
                else True
            ),
            "data_quality": (
                is_validatable(self.data_quality)
                if self.data_quality and hasattr(self.data_quality, "validate")
                else True
            ),
            "pricing_plans": (
                is_validatable(self.pricing_plans)
                if self.pricing_plans and hasattr(self.pricing_plans, "validate")
                else True
            ),
            "license": (
                is_validatable(self.license)
                if self.license and hasattr(self.license, "validate")
                else True
            ),
            "data_access": (
                is_validatable(self.data_access)
                if self.data_access and hasattr(self.data_access, "validate")
                else True
            ),
            "data_holder": (
                is_validatable(self.data_holder)
                if self.data_holder and hasattr(self.data_holder, "validate")
                else True
            ),
            "payment_gateways": (
                is_validatable(self.payment_gateways)
                if self.payment_gateways and hasattr(self.payment_gateways, "validate")
                else True
            ),
        }
        return results

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            "schema": self.schema,
            "version": self.version,
            "product": asdict(self.product_details),
        }

        # Convert snake_case back to camelCase for spec compliance
        product = result["product"]
        self._convert_snake_to_camel(product, self.PRODUCT_DETAILS_MAPPING)

        # Add optional components
        if self.product_strategy:
            ps_dict = asdict(self.product_strategy)
            self._convert_snake_to_camel(ps_dict, self.PRODUCT_STRATEGY_MAPPING)
            # Convert nested KPI objects
            if ps_dict.get("contributesToKPI"):
                self._convert_snake_to_camel(ps_dict["contributesToKPI"], self.KPI_MAPPING)
            if ps_dict.get("productKPIs"):
                for kpi in ps_dict["productKPIs"]:
                    self._convert_snake_to_camel(kpi, self.KPI_MAPPING)
            if ps_dict.get("relatedKPIs"):
                for kpi in ps_dict["relatedKPIs"]:
                    self._convert_snake_to_camel(kpi, self.KPI_MAPPING)
            product["productStrategy"] = ps_dict
        if self.data_contract:
            dc_dict = asdict(self.data_contract)
            self._convert_snake_to_camel(dc_dict, self.DATA_CONTRACT_MAPPING)
            product["dataContract"] = dc_dict
        if self.sla:
            product["SLA"] = asdict(self.sla)
        if self.data_quality:
            product["dataQuality"] = asdict(self.data_quality)
        if self.data_access:
            da_dict = {"default": asdict(self.data_access.default)}
            # Convert snake_case back to camelCase for spec compliance
            self._convert_snake_to_camel(da_dict["default"], self.DATA_ACCESS_MAPPING)

            # Add additional methods
            for key, method in self.data_access.additional_methods.items():
                method_dict = asdict(method)
                self._convert_snake_to_camel(method_dict, self.DATA_ACCESS_MAPPING)
                da_dict[key] = method_dict

            product["dataAccess"] = da_dict
        if self.license:
            license_dict = asdict(self.license)
            self._convert_snake_to_camel(license_dict, self.LICENSE_MAPPING)
            product["license"] = license_dict
        if self.data_holder:
            dh_dict = asdict(self.data_holder)
            self._convert_snake_to_camel(dh_dict, self.DATA_HOLDER_MAPPING)
            product["dataHolder"] = dh_dict
        if self.pricing_plans:
            pp_dict = {"plans": []}
            for plan in self.pricing_plans.plans:
                plan_dict = asdict(plan)
                self._convert_snake_to_camel(plan_dict, self.PRICING_PLAN_MAPPING)
                pp_dict["plans"].append(plan_dict)
            product["pricingPlans"] = pp_dict

        if self.payment_gateways:
            pg_dict = {"gateways": []}
            for gateway in self.payment_gateways.gateways:
                gateway_dict = asdict(gateway)
                self._convert_snake_to_camel(gateway_dict, self.PAYMENT_GATEWAY_MAPPING)
                pg_dict["gateways"].append(gateway_dict)
            product["paymentGateways"] = pg_dict

        # Add extensions (x- prefixed fields)
        if self.extensions:
            product.update(self.extensions.extensions)

        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string with caching"""
        current_hash = self._generate_hash()
        cache_key = f"json_{indent}"

        if (
            current_hash in self._serialization_cache
            and cache_key in self._serialization_cache
        ):
            return self._serialization_cache[cache_key]

        result = json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
        self._serialization_cache[cache_key] = result
        return result

    def to_yaml(self) -> str:
        """Convert to YAML string with caching"""
        current_hash = self._generate_hash()
        cache_key = "yaml"

        if (
            current_hash in self._serialization_cache
            and cache_key in self._serialization_cache
        ):
            return self._serialization_cache[cache_key]

        result = yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)
        self._serialization_cache[cache_key] = result
        return result

    def save(self, file_path: Union[str, Path], format: str = "auto") -> None:
        """
        Save to file

        Args:
            file_path: Path to save file
            format: Format to use ('json', 'yaml', or 'auto' to detect from extension)
        """
        path = Path(file_path)

        if format == "auto":
            if path.suffix.lower() in [".yaml", ".yml"]:
                format = "yaml"
            else:
                format = "json"

        if format == "yaml":
            content = self.to_yaml()
        else:
            content = self.to_json()

        path.write_text(content, encoding="utf-8")

    def add_data_contract(
        self,
        contract_url: Optional[str] = None,
        spec: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        type: Optional[str] = None,
        contract_version: Optional[str] = None,
        ref: Optional[str] = None,
    ) -> None:
        """Add or update data contract"""
        self.data_contract = DataContract(
            id=id,
            type=type,
            contract_version=contract_version,
            contract_url=contract_url,
            spec=spec,
            ref=ref,
        )
        self._invalidate_cache()

    def add_sla(self, profiles: Optional[Dict[str, Any]] = None) -> None:
        """Add or update SLA"""
        if profiles is None:
            profiles = {}
        self.sla = SLA(profiles=profiles)
        self._invalidate_cache()

    def add_license(self, scope_of_use: str, **kwargs) -> None:
        """Add or update license"""
        self.license = License(scope_of_use=scope_of_use, **kwargs)
        self._invalidate_cache()

    def add_data_access(
        self, default_method: DataAccessMethod, **additional_methods
    ) -> None:
        """Add or update data access methods"""
        self.data_access = DataAccess(
            default=default_method, additional_methods=additional_methods
        )
        self._invalidate_cache()

    def __str__(self) -> str:
        return f"OpenDataProduct(name='{self.product_details.name}', id='{self.product_details.product_id}')"

    def __repr__(self) -> str:
        return self.__str__()
