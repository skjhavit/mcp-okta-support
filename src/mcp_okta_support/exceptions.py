"""Custom exceptions for MCP Okta Support."""

from typing import Any, Dict, Optional


class MCPOktaSupportError(Exception):
    """Base exception for MCP Okta Support."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class OktaAPIError(MCPOktaSupportError):
    """Exception raised when Okta API calls fail."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.error_code = error_code


class AuthenticationError(OktaAPIError):
    """Exception raised for authentication failures."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)


class AuthorizationError(OktaAPIError):
    """Exception raised for authorization failures."""

    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, **kwargs)


class RateLimitError(OktaAPIError):
    """Exception raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class UserNotFoundError(OktaAPIError):
    """Exception raised when a user is not found."""

    def __init__(self, user_identifier: str, **kwargs):
        message = f"User not found: {user_identifier}"
        super().__init__(message, **kwargs)
        self.user_identifier = user_identifier


class ApplicationNotFoundError(OktaAPIError):
    """Exception raised when an application is not found."""

    def __init__(self, app_identifier: str, **kwargs):
        message = f"Application not found: {app_identifier}"
        super().__init__(message, **kwargs)
        self.app_identifier = app_identifier


class ValidationError(MCPOktaSupportError):
    """Exception raised for input validation errors."""

    def __init__(self, field: str, value: Any, reason: str, **kwargs):
        message = f"Validation failed for {field}: {reason}"
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        self.reason = reason


class ConfigurationError(MCPOktaSupportError):
    """Exception raised for configuration errors."""

    def __init__(self, setting: str, reason: str, **kwargs):
        message = f"Configuration error for {setting}: {reason}"
        super().__init__(message, **kwargs)
        self.setting = setting
        self.reason = reason


class MCPToolError(MCPOktaSupportError):
    """Exception raised when MCP tool execution fails."""

    def __init__(self, tool_name: str, reason: str, **kwargs):
        message = f"Tool {tool_name} failed: {reason}"
        super().__init__(message, **kwargs)
        self.tool_name = tool_name
        self.reason = reason


def handle_okta_api_error(response_status: int, response_data: Dict[str, Any]) -> OktaAPIError:
    """Convert Okta API error responses to appropriate exceptions.

    Args:
        response_status: HTTP status code
        response_data: Response body containing error details

    Returns:
        Appropriate OktaAPIError subclass
    """
    error_summary = response_data.get("errorSummary", "Unknown error")
    error_code = response_data.get("errorCode")
    error_causes = response_data.get("errorCauses", [])

    details = {
        "status_code": response_status,
        "error_code": error_code,
        "error_causes": error_causes,
        "response_data": response_data,
    }

    if response_status == 401:
        return AuthenticationError(error_summary, **details)
    elif response_status == 403:
        return AuthorizationError(error_summary, **details)
    elif response_status == 404:
        if "user" in error_summary.lower():
            return UserNotFoundError("unknown", **details)
        elif "app" in error_summary.lower():
            return ApplicationNotFoundError("unknown", **details)
        return OktaAPIError(error_summary, **details)
    elif response_status == 429:
        # Extract retry-after from headers if available
        return RateLimitError(error_summary, **details)
    else:
        return OktaAPIError(error_summary, **details)