#!/usr/bin/env python3
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
Comprehensive example demonstrating ODPS v4.1 features

This example showcases the new features introduced in ODPS v4.1:
- ProductStrategy: Connecting data products to business objectives
- KPI: Key Performance Indicators for business alignment
- AI agent integration via MCP
- Enhanced $ref support for component referencing
"""

from open_data_products.odps import OpenDataProduct
from open_data_products.odps.models import (
    ProductDetails,
    ProductStrategy,
    KPI,
    DataAccess,
    DataAccessMethod,
    DataHolder,
    License,
)


def create_v41_example():
    """Create a comprehensive ODPS v4.1 example document"""

    # 1. Create core product details
    product_details = ProductDetails(
        name="Customer Analytics Data Product",
        product_id="customer-analytics-v2",
        visibility="organisation",
        status="production",
        type="dataset",
        description="Real-time customer behavior analytics with predictive insights",
        value_proposition="Enable data-driven decision making to reduce customer churn by 25%",
        categories=["analytics", "customer-insights", "predictive"],
        tags=["customer", "churn", "retention", "predictive-analytics"],
        language=["en"],
        homepage="https://example.com/products/customer-analytics",
        created="2024-01-15",
        updated="2024-11-07",
        product_version="2.0.0",
        version_notes="Added ProductStrategy alignment and AI agent access",
    )

    # 2. Create OpenDataProduct instance
    product = OpenDataProduct(product_details)

    # 3. Add ProductStrategy (NEW in v4.1)
    # This connects the data product to business intent and KPIs
    product_strategy = ProductStrategy(
        objectives=[
            "Reduce customer churn by identifying at-risk customers early",
            "Improve customer lifetime value through targeted retention campaigns",
            "Enable predictive analytics for proactive customer engagement",
        ],
        contributes_to_kpi=KPI(
            name="Customer Retention Rate",
            id="kpi-retention-001",
            unit="percentage",
            target=95,
            direction="increase",
            calculation="(Customers at end of period / Customers at start) * 100",
            description="Primary business KPI measuring customer retention",
        ),
        product_kpis=[
            KPI(
                name="Churn Prediction Accuracy",
                id="kpi-churn-accuracy",
                unit="percentage",
                target=85,
                direction="at_least",
                calculation="(Correct predictions / Total predictions) * 100",
                description="Measures accuracy of churn prediction model",
            ),
            KPI(
                name="Early Warning Detection Rate",
                id="kpi-early-warning",
                unit="percentage",
                target=90,
                direction="at_least",
                calculation="(Customers flagged 30+ days before churn / Total churned) * 100",
                description="Percentage of churns predicted with 30+ day lead time",
            ),
        ],
        related_kpis=[
            KPI(
                name="Cost per Retained Customer",
                id="kpi-retention-cost",
                unit="currency",
                target=50,
                direction="at_most",
                calculation="Total retention campaign cost / Number retained",
                description="Financial efficiency of retention efforts",
            ),
        ],
        strategic_alignment=[
            "Corporate Strategy 2024: Customer-First Initiative",
            "Digital Transformation Roadmap Q4",
            "Data Governance Policy v3.2",
        ],
    )
    product.product_strategy = product_strategy

    # 4. Add Data Access with AI agent support (NEW in v4.1)
    default_access = DataAccessMethod(
        name={"en": "REST API Access"},
        description={"en": "Standard REST API for programmatic access"},
        output_port_type="API",
        format="JSON",
        access_url="https://api.example.com/customer-analytics/v2",
        authentication_method="bearer-token",
        documentation_url="https://docs.example.com/customer-analytics",
    )

    # AI Agent Access - NEW in v4.1
    ai_agent_access = DataAccessMethod(
        name={"en": "AI Agent Access"},
        description={"en": "Model Context Protocol access for AI agents"},
        output_port_type="AI",  # NEW: AI output port type
        format="MCP",  # NEW: MCP (Model Context Protocol) format
        access_url="mcp://api.example.com/customer-analytics/agent",
        authentication_method="bearer-token",
        specification={
            "protocol": "MCP",
            "version": "1.0",
            "capabilities": [
                "query",
                "analyze",
                "predict",
            ],
            "agent_description": "Autonomous agent for customer churn analysis",
        },
        documentation_url="https://docs.example.com/mcp-integration",
    )

    product.data_access = DataAccess(
        default=default_access,
        additional_methods={
            "aiAgent": ai_agent_access,
        },
    )

    # 5. Add Data Holder information
    product.data_holder = DataHolder(
        name="Acme Corporation Data Team",
        email="data-team@example.com",
        url="https://example.com/data-team",
        phone_number="+61444123456",
        contact_person="Jane Smith",
        contact_email="jane.smith@example.com",
        organizational_description="Enterprise data platform team managing customer analytics",
    )

    # 6. Add License information
    product.license = License(
        scope_of_use="internal",
        geographical_area=["US", "EU", "UK"],
        permanent=False,
        exclusive=False,
        valid_from="2024-01-15",
        valid_until="2025-12-31",
        license_name="Internal Data Use License",
        scope_details="Internal use for customer retention analysis only",
    )

    return product


def main():
    """Main function to demonstrate v4.1 features"""

    print("=" * 80)
    print("ODPS v4.1 Example - ProductStrategy & AI Agent Integration")
    print("=" * 80)
    print()

    # Create the example product
    print("Creating ODPS v4.1 data product...")
    product = create_v41_example()
    print("✓ Product created successfully")
    print()

    # Validate the product
    print("Validating ODPS v4.1 document...")
    is_valid = product.validate()
    if is_valid:
        print("✓ Validation passed - document is v4.1 compliant")
    else:
        print("✗ Validation failed")
        errors = product.get_validation_errors()
        for error in errors:
            print(f"  - {error}")
    print()

    # Display v4.1 specific features
    print("=" * 80)
    print("V4.1 FEATURES OVERVIEW")
    print("=" * 80)
    print()

    print("1. PRODUCT STRATEGY")
    print("-" * 40)
    if product.product_strategy:
        ps = product.product_strategy
        print(f"   Objectives: {len(ps.objectives)}")
        for i, obj in enumerate(ps.objectives, 1):
            print(f"     {i}. {obj}")
        print()
        if ps.contributes_to_kpi:
            kpi = ps.contributes_to_kpi
            print(f"   Primary KPI: {kpi.name}")
            print(f"     Target: {kpi.target} {kpi.unit}")
            print(f"     Direction: {kpi.direction}")
        print()
        print(f"   Product KPIs: {len(ps.product_kpis)}")
        for kpi in ps.product_kpis:
            print(f"     - {kpi.name}: {kpi.target} {kpi.unit} ({kpi.direction})")
        print()

    print("2. AI AGENT INTEGRATION")
    print("-" * 40)
    if product.data_access:
        for method_name, method in product.data_access.additional_methods.items():
            if method.output_port_type == "AI":
                print(f"   Method: {method_name}")
                print(f"   Output Port: {method.output_port_type} (NEW in v4.1)")
                print(f"   Format: {method.format}")
                print(f"   URL: {method.access_url}")
                print()

    print("3. SCHEMA VERSION")
    print("-" * 40)
    print(f"   Schema: {product.schema}")
    print(f"   Version: {product.version}")
    print()

    # Export to JSON
    print("=" * 80)
    print("EXPORTING TO JSON")
    print("=" * 80)
    print()

    json_output = product.to_json(indent=2)
    output_file = "customer_analytics_v41.json"
    product.save(output_file)
    print(f"✓ Saved to {output_file}")
    print()

    # Show a sample of the JSON
    print("Sample JSON output (first 50 lines):")
    print("-" * 40)
    lines = json_output.split("\n")
    for line in lines[:50]:
        print(line)
    if len(lines) > 50:
        print(f"... ({len(lines) - 50} more lines)")
    print()

    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
