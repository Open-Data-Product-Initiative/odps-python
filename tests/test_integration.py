"""Integration tests that work with actual implementation."""

import pytest
import json
import tempfile
from pathlib import Path

from odps import OpenDataProduct
from odps.models import ProductDetails, UseCase


class TestIntegration:
    """Simple integration tests to verify the library works."""

    def test_create_basic_product(self):
        """Test creating a basic ODPS product."""
        details = ProductDetails(
            name="Test Dataset",
            product_id="test-001",
            visibility="public",
            status="draft",
            type="dataset"
        )
        
        product = OpenDataProduct(details)
        
        # Basic assertions
        assert product.product_details.name == "Test Dataset"
        assert product.product_details.product_id == "test-001"
        assert product.schema == "https://opendataproducts.org/v4.1/schema/odps.json"
        assert product.version == "4.1"

    def test_product_with_use_case(self):
        """Test product with use cases."""
        use_case = UseCase(
            title="Analytics",
            description="For data analysis"
        )
        
        details = ProductDetails(
            name="Analytics Dataset",
            product_id="analytics-001",
            visibility="public",
            status="production",
            type="dataset",
            use_cases=[use_case]
        )
        
        product = OpenDataProduct(details)
        
        assert len(product.product_details.use_cases) == 1
        assert product.product_details.use_cases[0].title == "Analytics"

    def test_json_serialization(self):
        """Test JSON serialization works."""
        details = ProductDetails(
            name="JSON Test",
            product_id="json-001",
            visibility="public",
            status="draft",
            type="dataset"
        )
        
        product = OpenDataProduct(details)
        json_str = product.to_json()
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["product"]["name"] == "JSON Test"
        assert data["product"]["productID"] == "json-001"

    def test_yaml_serialization(self):
        """Test YAML serialization works."""
        details = ProductDetails(
            name="YAML Test",
            product_id="yaml-001", 
            visibility="public",
            status="draft",
            type="dataset"
        )
        
        product = OpenDataProduct(details)
        yaml_str = product.to_yaml()
        
        # Should contain expected content
        assert "YAML Test" in yaml_str
        assert "yaml-001" in yaml_str

    def test_roundtrip_json(self):
        """Test JSON roundtrip serialization."""
        details = ProductDetails(
            name="Roundtrip Test",
            product_id="roundtrip-001",
            visibility="public",
            status="draft",
            type="dataset"
        )
        
        original = OpenDataProduct(details)
        json_str = original.to_json()
        restored = OpenDataProduct.from_json(json_str)
        
        assert restored.product_details.name == original.product_details.name
        assert restored.product_details.product_id == original.product_details.product_id

    def test_save_and_load(self):
        """Test saving to file and loading back."""
        details = ProductDetails(
            name="File Test",
            product_id="file-001",
            visibility="public", 
            status="draft",
            type="dataset"
        )
        
        original = OpenDataProduct(details)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            original.save(tmp_path)
            loaded = OpenDataProduct.from_file(tmp_path)
            
            assert loaded.product_details.name == "File Test"
            assert loaded.product_details.product_id == "file-001"
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_validation_passes(self):
        """Test that valid product passes validation."""
        details = ProductDetails(
            name="Valid Product",
            product_id="valid-001",
            visibility="public",
            status="production", 
            type="dataset"
        )
        
        product = OpenDataProduct(details)
        
        # Should validate successfully
        result = product.validate()
        assert result is True

    def test_demo_files_exist_and_load(self):
        """Test that demo files can be loaded if they exist."""
        demo_json = Path("examples/demo_product.json")
        demo_yaml = Path("examples/demo_product.yaml")
        
        if demo_json.exists():
            product = OpenDataProduct.from_file(demo_json)
            assert isinstance(product, OpenDataProduct)
            assert product.product_details.name is not None
            print(f"✓ Successfully loaded {demo_json}")
        
        if demo_yaml.exists():
            product = OpenDataProduct.from_file(demo_yaml)
            assert isinstance(product, OpenDataProduct)
            assert product.product_details.name is not None
            print(f"✓ Successfully loaded {demo_yaml}")

    def test_complex_product(self):
        """Test creating a more complex product with multiple features."""
        details = ProductDetails(
            name="Complex Analytics Dataset",
            product_id="complex-001",
            visibility="organisation",
            status="production",
            type="dataset",
            description="A comprehensive dataset for analytics",
            categories=["analytics", "sales"],
            tags=["quarterly", "revenue", "b2b"],
            language=["en", "es"],
            standards=["ISO 8601"]
        )
        
        product = OpenDataProduct(details)
        
        # Should serialize and validate
        json_str = product.to_json()
        yaml_str = product.to_yaml()
        result = product.validate()
        
        assert len(json_str) > 100  # Should have substantial content
        assert len(yaml_str) > 100
        assert result is True
        assert "analytics" in product.product_details.categories
        assert "en" in product.product_details.language
