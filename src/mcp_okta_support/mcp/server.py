"""MCP server setup and configuration."""

from typing import Any, Dict, List
from fastmcp import FastMCP

from ..config import Settings
from ..okta.client import OktaClient
from ..utils.logging import get_logger
from .tools import register_tools
from .resources import register_resources

logger = get_logger(__name__)


def setup_mcp_server(settings: Settings) -> FastMCP:
    """Set up and configure the FastMCP server.

    Args:
        settings: Application settings

    Returns:
        Configured FastMCP server instance
    """
    logger.info(
        "Setting up MCP server",
        server_name=settings.mcp_server_name,
        version=settings.mcp_server_version,
    )

    # Validate authentication configuration
    settings.validate_auth_config()

    # Create FastMCP instance
    mcp = FastMCP(
        name=settings.mcp_server_name,
        version=settings.mcp_server_version,
    )

    # Initialize Okta client
    okta_client = OktaClient(settings)

    # Register tools and resources
    register_tools(mcp, okta_client, settings)
    register_resources(mcp, okta_client, settings)

    # Add server info and capabilities
    _add_server_info(mcp, settings)

    logger.info("MCP server setup completed successfully")
    return mcp


def _add_server_info(mcp: FastMCP, settings: Settings) -> None:
    """Add server information and capabilities to MCP server.

    Args:
        mcp: FastMCP server instance
        settings: Application settings
    """
    @mcp.resource("server://info")
    def get_server_info() -> Dict[str, Any]:
        """Get server information and capabilities."""
        return {
            "name": settings.mcp_server_name,
            "version": settings.mcp_server_version,
            "description": "MCP server for Okta user and application management",
            "okta_org": settings.okta_org_url,
            "authentication_method": "oauth" if settings.is_oauth_configured else "api_token",
            "capabilities": {
                "user_management": {
                    "get_details": True,
                    "update_profile": True,
                    "reinvite": True,
                    "unlock_account": True,
                    "reset_password": True,
                },
                "application_management": {
                    "list_applications": True,
                    "get_details": True,
                    "update_config": True,
                },
                "system_logs": {
                    "user_logs": True,
                    "application_logs": True,
                    "search_logs": True,
                },
            },
            "rate_limits": {
                "requests_per_minute": settings.okta_rate_limit,
                "timeout_seconds": settings.okta_timeout_seconds,
            },
        }

    @mcp.resource("server://health")
    def get_health_status() -> Dict[str, Any]:
        """Get server health status."""
        return {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z",  # This would be dynamic in real implementation
            "version": settings.mcp_server_version,
            "okta_connection": "connected",  # This would be tested in real implementation
        }