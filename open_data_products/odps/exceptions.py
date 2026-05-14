"""Exception hierarchy for the ODPS library.

Trimmed to the five classes actually raised in the codebase. Removed
21 unused subclasses (component-specific, file permission, schema version,
serialization, network, configuration, extension) — none were caught
externally and ``except ODPSError`` covers their base case if they ever
need to come back.
"""

from typing import Any, Dict, List, Optional


class ODPSError(Exception):
    """Base exception class for all ODPS library errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
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
        details: Dict[str, Any] = {}
        if field:
            details["field"] = field
        if errors:
            details["error_count"] = len(errors)

        super().__init__(message, details)
        self.errors = errors or []
        self.field = field

    @classmethod
    def from_errors(cls, errors: List[str]) -> "ODPSValidationError":
        message = f"Validation failed with {len(errors)} error(s): {'; '.join(errors)}"
        return cls(message, errors)

    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.details["error_count"] = len(self.errors)


class ODPSJSONParsingError(ODPSError):
    """Raised when JSON parsing fails."""

    def __init__(self, message: str, line_number: Optional[int] = None):
        details: Dict[str, Any] = {"format": "json"}
        if line_number is not None:
            details["line"] = line_number
        super().__init__(f"JSON parsing error: {message}", details)
        self.line_number = line_number


class ODPSYAMLParsingError(ODPSError):
    """Raised when YAML parsing fails."""

    def __init__(self, message: str, line_number: Optional[int] = None):
        details: Dict[str, Any] = {"format": "yaml"}
        if line_number is not None:
            details["line"] = line_number
        super().__init__(f"YAML parsing error: {message}", details)
        self.line_number = line_number


class ODPSFileNotFoundError(ODPSError, FileNotFoundError):
    """Raised when an ODPS file is not found."""

    def __init__(self, file_path: str):
        super().__init__(f"ODPS file not found: {file_path}", {"file_path": file_path})
        self.file_path = file_path
