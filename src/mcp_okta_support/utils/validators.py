"""Input validation utilities."""

import re
from typing import Any, List, Optional, Tuple
from email_validator import validate_email, EmailNotValidError

from ..exceptions import ValidationError


def validate_user_identifier(identifier: str) -> Tuple[str, str]:
    """Validate and normalize user identifier.

    Args:
        identifier: User ID, email, or login name

    Returns:
        Tuple of (normalized_identifier, identifier_type)

    Raises:
        ValidationError: If identifier is invalid
    """
    if not identifier or not identifier.strip():
        raise ValidationError("user_identifier", identifier, "Cannot be empty")

    identifier = identifier.strip()

    # Check if it's an Okta user ID (starts with 00u)
    if re.match(r'^00u[a-zA-Z0-9]{17}$', identifier):
        return identifier, "user_id"

    # Check if it's an email address
    try:
        validated = validate_email(identifier)
        return validated.email, "email"
    except EmailNotValidError:
        pass

    # Check if it's a valid login name (alphanumeric, dots, underscores, hyphens)
    if re.match(r'^[a-zA-Z0-9._-]+$', identifier):
        return identifier, "login"

    raise ValidationError(
        "user_identifier",
        identifier,
        "Must be a valid user ID, email address, or login name"
    )


def validate_application_identifier(identifier: str) -> Tuple[str, str]:
    """Validate and normalize application identifier.

    Args:
        identifier: Application ID, name, or label

    Returns:
        Tuple of (normalized_identifier, identifier_type)

    Raises:
        ValidationError: If identifier is invalid
    """
    if not identifier or not identifier.strip():
        raise ValidationError("app_identifier", identifier, "Cannot be empty")

    identifier = identifier.strip()

    # Check if it's an Okta app ID (starts with 0oa)
    if re.match(r'^0oa[a-zA-Z0-9]{17}$', identifier):
        return identifier, "app_id"

    # Check if it's a valid app name (lowercase, alphanumeric, underscores, hyphens)
    if re.match(r'^[a-zA-Z0-9_-]+$', identifier):
        return identifier, "app_name"

    # Otherwise treat as app label (can contain spaces and special characters)
    return identifier, "app_label"


def validate_email_address(email: str) -> str:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Normalized email address

    Raises:
        ValidationError: If email is invalid
    """
    if not email or not email.strip():
        raise ValidationError("email", email, "Cannot be empty")

    try:
        validated = validate_email(email.strip())
        return validated.email
    except EmailNotValidError as e:
        raise ValidationError("email", email, str(e))


def validate_okta_org_url(url: str) -> str:
    """Validate Okta organization URL.

    Args:
        url: Okta org URL to validate

    Returns:
        Normalized URL

    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not url.strip():
        raise ValidationError("okta_org_url", url, "Cannot be empty")

    url = url.strip().rstrip('/')

    if not url.startswith('https://'):
        raise ValidationError("okta_org_url", url, "Must start with https://")

    if not (url.endswith('.okta.com') or url.endswith('.oktapreview.com')):
        raise ValidationError(
            "okta_org_url",
            url,
            "Must end with .okta.com or .oktapreview.com"
        )

    # Check for valid domain format
    domain_pattern = r'^https://[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]\.(okta|oktapreview)\.com$'
    if not re.match(domain_pattern, url):
        raise ValidationError(
            "okta_org_url",
            url,
            "Invalid Okta domain format"
        )

    return url


def validate_api_token(token: str) -> str:
    """Validate Okta API token format.

    Args:
        token: API token to validate

    Returns:
        Token if valid

    Raises:
        ValidationError: If token is invalid
    """
    if not token or not token.strip():
        raise ValidationError("api_token", token, "Cannot be empty")

    token = token.strip()

    # Okta API tokens are typically 40 characters, alphanumeric + some special chars
    if len(token) < 20:
        raise ValidationError("api_token", token, "Token appears too short")

    if len(token) > 100:
        raise ValidationError("api_token", token, "Token appears too long")

    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', token):
        raise ValidationError(
            "api_token",
            token,
            "Token contains invalid characters"
        )

    return token


def validate_oauth_client_id(client_id: str) -> str:
    """Validate OAuth client ID format.

    Args:
        client_id: Client ID to validate

    Returns:
        Client ID if valid

    Raises:
        ValidationError: If client ID is invalid
    """
    if not client_id or not client_id.strip():
        raise ValidationError("client_id", client_id, "Cannot be empty")

    client_id = client_id.strip()

    # Okta client IDs are typically 20 characters, alphanumeric
    if len(client_id) < 10:
        raise ValidationError("client_id", client_id, "Client ID appears too short")

    if len(client_id) > 50:
        raise ValidationError("client_id", client_id, "Client ID appears too long")

    if not re.match(r'^[a-zA-Z0-9_-]+$', client_id):
        raise ValidationError(
            "client_id",
            client_id,
            "Client ID contains invalid characters"
        )

    return client_id


def validate_oauth_scopes(scopes: List[str]) -> List[str]:
    """Validate OAuth scopes.

    Args:
        scopes: List of OAuth scopes

    Returns:
        Validated scopes

    Raises:
        ValidationError: If scopes are invalid
    """
    if not scopes:
        raise ValidationError("scopes", scopes, "At least one scope is required")

    validated_scopes = []
    valid_scope_pattern = r'^[a-zA-Z0-9._:-]+$'

    for scope in scopes:
        if not isinstance(scope, str) or not scope.strip():
            raise ValidationError("scopes", scope, "Scope cannot be empty")

        scope = scope.strip()

        if not re.match(valid_scope_pattern, scope):
            raise ValidationError(
                "scopes",
                scope,
                "Scope contains invalid characters"
            )

        validated_scopes.append(scope)

    return validated_scopes


def validate_log_query(query: str) -> str:
    """Validate system log search query.

    Args:
        query: Search query to validate

    Returns:
        Validated query

    Raises:
        ValidationError: If query is invalid
    """
    if not query or not query.strip():
        raise ValidationError("query", query, "Cannot be empty")

    query = query.strip()

    # Check for potential injection attacks
    dangerous_patterns = [
        r'[;\'"\\]',  # SQL-like injection characters
        r'<script',   # XSS attempts
        r'javascript:',  # JavaScript injection
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValidationError(
                "query",
                query,
                "Query contains potentially dangerous characters"
            )

    return query


def validate_positive_integer(value: Any, field_name: str, min_val: int = 1, max_val: int = None) -> int:
    """Validate positive integer value.

    Args:
        value: Value to validate
        field_name: Name of the field being validated
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Validated integer

    Raises:
        ValidationError: If value is invalid
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(field_name, value, "Must be a valid integer")

    if int_value < min_val:
        raise ValidationError(field_name, value, f"Must be at least {min_val}")

    if max_val is not None and int_value > max_val:
        raise ValidationError(field_name, value, f"Must be at most {max_val}")

    return int_value


def validate_iso_timestamp(timestamp: str) -> str:
    """Validate ISO timestamp format.

    Args:
        timestamp: Timestamp string to validate

    Returns:
        Validated timestamp

    Raises:
        ValidationError: If timestamp is invalid
    """
    if not timestamp or not timestamp.strip():
        raise ValidationError("timestamp", timestamp, "Cannot be empty")

    timestamp = timestamp.strip()

    # Basic ISO 8601 format validation
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'
    if not re.match(iso_pattern, timestamp):
        raise ValidationError(
            "timestamp",
            timestamp,
            "Must be in ISO 8601 format (e.g., 2024-01-01T00:00:00Z)"
        )

    return timestamp


def sanitize_log_output(text: str) -> str:
    """Sanitize text for safe logging.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text with sensitive data removed
    """
    if not text:
        return text

    # Remove potential API tokens
    text = re.sub(r'(SSWS\s+)[a-zA-Z0-9_-]{20,}', r'\1[REDACTED]', text)

    # Remove potential OAuth tokens
    text = re.sub(r'(Bearer\s+)[a-zA-Z0-9_-]{20,}', r'\1[REDACTED]', text)

    # Remove potential passwords
    text = re.sub(r'(["\']?password["\']?\s*[:=]\s*["\']?)[^"\'\\s]+', r'\1[REDACTED]', text, flags=re.IGNORECASE)

    # Remove potential client secrets
    text = re.sub(r'(["\']?client_secret["\']?\s*[:=]\s*["\']?)[^"\'\\s]+', r'\1[REDACTED]', text, flags=re.IGNORECASE)

    return text