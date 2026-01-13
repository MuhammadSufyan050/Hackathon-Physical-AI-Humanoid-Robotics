"""Error handling utilities for the Book Q&A Retrieval Agent."""

import logging
from typing import Optional
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception class for agent-related errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict:
        """Convert the error to a dictionary representation."""
        return {
            "error": self.message,
            "code": self.error_code,
            "details": self.details
        }


class ValidationError(AgentError):
    """Exception raised for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field = field
        if field:
            self.details["field"] = field


class RetrievalError(AgentError):
    """Exception raised for retrieval-related errors."""

    def __init__(self, message: str, query: Optional[str] = None):
        super().__init__(message, error_code="RETRIEVAL_ERROR")
        self.query = query
        if query:
            self.details["query"] = query


class ConnectionError(AgentError):
    """Exception raised for connection-related errors."""

    def __init__(self, message: str, service: Optional[str] = None):
        super().__init__(message, error_code="CONNECTION_ERROR")
        self.service = service
        if service:
            self.details["service"] = service


class ConfigurationError(AgentError):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, error_code="CONFIGURATION_ERROR")
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


def handle_error(error: Exception, context: str = "") -> dict:
    """
    Generic error handler that logs the error and returns a safe response.

    Args:
        error: The exception to handle
        context: Context information about where the error occurred

    Returns:
        Dictionary with error information safe for return to users
    """
    error_msg = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    logger.error(error_msg, exc_info=True)

    # Return a safe error response without exposing internal details
    if isinstance(error, AgentError):
        return error.to_dict()
    else:
        # For unexpected errors, return a generic message
        return {
            "error": "An unexpected error occurred. Please try again later.",
            "code": "UNEXPECTED_ERROR",
            "details": {"context": context} if context else {}
        }


def validate_response_content(content: str, max_length: int = 10000) -> bool:
    """
    Validate that a response content is safe and appropriate.

    Args:
        content: The content to validate
        max_length: Maximum allowed length

    Returns:
        True if content is valid, raises ValidationError if not
    """
    if not content:
        raise ValidationError("Response content cannot be empty")

    if len(content) > max_length:
        raise ValidationError(f"Response content exceeds maximum length of {max_length} characters")

    # Check for potentially problematic patterns
    if "```" in content and content.count("```") % 2 != 0:
        logger.warning("Response contains unbalanced code block markers")

    return True