"""Configuration management using Pydantic settings."""

from typing import Optional, List
from pydantic import BaseSettings, validator, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Okta Configuration
    okta_org_url: str = Field(..., description="Okta organization URL")
    okta_api_token: Optional[str] = Field(None, description="Okta API token")

    # OAuth 2.0 Configuration (alternative to API token)
    okta_client_id: Optional[str] = Field(None, description="OAuth client ID")
    okta_client_secret: Optional[str] = Field(None, description="OAuth client secret")
    okta_scopes: List[str] = Field(
        default=["okta.users.manage", "okta.apps.manage", "okta.logs.read"],
        description="OAuth scopes"
    )

    # MCP Server Configuration
    mcp_server_name: str = Field(default="okta-support", description="MCP server name")
    mcp_server_version: str = Field(default="0.1.0", description="MCP server version")
    mcp_log_level: str = Field(default="INFO", description="Logging level")

    # Rate limiting and timeouts
    okta_rate_limit: int = Field(default=100, description="Requests per minute")
    okta_timeout_seconds: int = Field(default=30, description="Request timeout")

    # Development settings
    development_mode: bool = Field(default=False, description="Enable development mode")
    log_structured: bool = Field(default=True, description="Use structured logging")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("okta_org_url")
    def validate_okta_url(cls, v: str) -> str:
        """Ensure Okta URL is properly formatted."""
        if not v.startswith("https://"):
            raise ValueError("Okta org URL must start with https://")
        if not v.endswith(".okta.com") and not v.endswith(".oktapreview.com"):
            raise ValueError("Invalid Okta org URL format")
        return v.rstrip("/")

    @validator("okta_scopes", pre=True)
    def parse_scopes(cls, v):
        """Parse comma-separated scopes string into list."""
        if isinstance(v, str):
            return [scope.strip() for scope in v.split(",")]
        return v

    @validator("mcp_log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_upper

    def validate_auth_config(self) -> None:
        """Validate that either API token or OAuth credentials are provided."""
        if not self.okta_api_token and not (self.okta_client_id and self.okta_client_secret):
            raise ValueError(
                "Either OKTA_API_TOKEN or both OKTA_CLIENT_ID and OKTA_CLIENT_SECRET must be provided"
            )

    @property
    def log_level(self) -> str:
        """Get the log level for the application."""
        return self.mcp_log_level

    @property
    def is_oauth_configured(self) -> bool:
        """Check if OAuth credentials are configured."""
        return bool(self.okta_client_id and self.okta_client_secret)

    @property
    def is_api_token_configured(self) -> bool:
        """Check if API token is configured."""
        return bool(self.okta_api_token)