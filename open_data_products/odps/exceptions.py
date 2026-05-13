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
Exception hierarchy for ODPS library
"""

from typing import List, Optional, Any, Dict


class ODPSError(Exception):
    """Base exception class for all ODPS library errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ODPSValidationError(ODPSError):
    """Raised when ODPS document validation fails."""

    def __init__(
        self,
        message: str,
        errors: Optional[List[str]] = None,
        field: Optional[str] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        if errors:
            details["error_count"] = len(errors)

        super().__init__(message, details)
        self.errors = errors or []
        self.field = field

    @classmethod
    def from_errors(cls, errors: List[str]) -> "ODPSValidationError":
        """Create validation error from list of error messages."""
        message = f"Validation failed with {len(errors)} error(s): {'; '.join(errors)}"
        return cls(message, errors)

    def add_error(self, error: str) -> None:
        """Add an additional error to the validation error."""
        self.errors.append(error)
        self.details["error_count"] = len(self.errors)


class ODPSFieldValidationError(ODPSValidationError):
    """Raised when a specific field fails validation."""

    def __init__(self, field: str, value: Any, message: str):
        super().__init__(f"Field '{field}' validation failed: {message}", field=field)
        self.value = value


class ODPSParsingError(ODPSError):
    """Raised when JSON/YAML parsing fails."""

    def __init__(
        self, message: str, format_type: str, line_number: Optional[int] = None
    ):
        details: Dict[str, Any] = {"format": format_type}
        if line_number is not None:
            details["line"] = line_number

        super().__init__(message, details)
        self.format_type = format_type
        self.line_number = line_number


class ODPSJSONParsingError(ODPSParsingError):
    """Raised when JSON parsing specifically fails."""

    def __init__(self, message: str, line_number: Optional[int] = None):
        super().__init__(f"JSON parsing error: {message}", "json", line_number)


class ODPSYAMLParsingError(ODPSParsingError):
    """Raised when YAML parsing specifically fails."""

    def __init__(self, message: str, line_number: Optional[int] = None):
        super().__init__(f"YAML parsing error: {message}", "yaml", line_number)


class ODPSFileError(ODPSError):
    """Base class for file-related errors."""

    def __init__(self, message: str, file_path: str):
        super().__init__(message, {"file_path": file_path})
        self.file_path = file_path


class ODPSFileNotFoundError(ODPSFileError, FileNotFoundError):
    """Raised when ODPS file is not found."""

    def __init__(self, file_path: str):
        message = f"ODPS file not found: {file_path}"
        super().__init__(message, file_path)


class ODPSFilePermissionError(ODPSFileError, PermissionError):
    """Raised when file permissions prevent reading/writing ODPS file."""

    def __init__(self, file_path: str, operation: str = "access"):
        message = f"Permission denied for {operation} operation on file: {file_path}"
        super().__init__(message, file_path)
        self.operation = operation


class ODPSSchemaError(ODPSError):
    """Raised when ODPS schema-related issues occur."""

    def __init__(self, message: str, schema_version: Optional[str] = None):
        details = {}
        if schema_version:
            details["schema_version"] = schema_version

        super().__init__(message, details)
        self.schema_version = schema_version


class ODPSSchemaVersionError(ODPSSchemaError):
    """Raised when unsupported ODPS schema version is encountered."""

    def __init__(self, found_version: str, supported_versions: List[str]):
        message = f"Unsupported schema version '{found_version}'. Supported versions: {', '.join(supported_versions)}"
        super().__init__(message, found_version)
        self.found_version = found_version
        self.supported_versions = supported_versions


class ODPSComponentError(ODPSError):
    """Raised when ODPS component-specific issues occur."""

    def __init__(self, message: str, component: str):
        super().__init__(message, {"component": component})
        self.component = component


class ODPSDataContractError(ODPSComponentError):
    """Raised when data contract issues occur."""

    def __init__(self, message: str):
        super().__init__(f"Data contract error: {message}", "dataContract")


class ODPSSLAError(ODPSComponentError):
    """Raised when SLA component issues occur."""

    def __init__(self, message: str):
        super().__init__(f"SLA error: {message}", "SLA")


class ODPSDataQualityError(ODPSComponentError):
    """Raised when data quality component issues occur."""

    def __init__(self, message: str):
        super().__init__(f"Data quality error: {message}", "dataQuality")


class ODPSLicenseError(ODPSComponentError):
    """Raised when license component issues occur."""

    def __init__(self, message: str):
        super().__init__(f"License error: {message}", "license")


class ODPSDataAccessError(ODPSComponentError):
    """Raised when data access component issues occur."""

    def __init__(self, message: str):
        super().__init__(f"Data access error: {message}", "dataAccess")


class ODPSDataHolderError(ODPSComponentError):
    """Raised when data holder component issues occur."""

    def __init__(self, message: str):
        super().__init__(f"Data holder error: {message}", "dataHolder")


class ODPSPricingError(ODPSComponentError):
    """Raised when pricing plans component issues occur."""

    def __init__(self, message: str):
        super().__init__(f"Pricing error: {message}", "pricingPlans")


class ODPSPaymentGatewayError(ODPSComponentError):
    """Raised when payment gateway component issues occur."""

    def __init__(self, message: str):
        super().__init__(f"Payment gateway error: {message}", "paymentGateways")


class ODPSSerializationError(ODPSError):
    """Raised when serialization issues occur."""

    def __init__(self, message: str, format_type: str):
        super().__init__(message, {"format": format_type})
        self.format_type = format_type


class ODPSJSONSerializationError(ODPSSerializationError):
    """Raised when JSON serialization fails."""

    def __init__(self, message: str):
        super().__init__(f"JSON serialization error: {message}", "json")


class ODPSYAMLSerializationError(ODPSSerializationError):
    """Raised when YAML serialization fails."""

    def __init__(self, message: str):
        super().__init__(f"YAML serialization error: {message}", "yaml")


class ODPSNetworkError(ODPSError):
    """Raised when network-related operations fail."""

    def __init__(
        self, message: str, url: Optional[str] = None, status_code: Optional[int] = None
    ):
        details = {}
        if url:
            details["url"] = url
        if status_code:
            details["status_code"] = status_code

        super().__init__(message, details)
        self.url = url
        self.status_code = status_code


class ODPSConfigurationError(ODPSError):
    """Raised when configuration issues occur."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(message, details)
        self.config_key = config_key


class ODPSExtensionError(ODPSError):
    """Raised when extension field issues occur."""

    def __init__(self, message: str, extension_key: str):
        super().__init__(message, {"extension_key": extension_key})
        self.extension_key = extension_key


# Convenience function to create appropriate validation errors
def create_field_error(
    field: str, value: Any, message: str
) -> ODPSFieldValidationError:
    """Create a field-specific validation error."""
    return ODPSFieldValidationError(field, value, message)


def create_component_error(component: str, message: str) -> ODPSComponentError:
    """Create a component-specific error."""
    component_error_map = {
        "dataContract": ODPSDataContractError,
        "SLA": ODPSSLAError,
        "dataQuality": ODPSDataQualityError,
        "license": ODPSLicenseError,
        "dataAccess": ODPSDataAccessError,
        "dataHolder": ODPSDataHolderError,
        "pricingPlans": ODPSPricingError,
        "paymentGateways": ODPSPaymentGatewayError,
    }

    error_class = component_error_map.get(component, ODPSComponentError)
    return error_class(message)
