"""MCP tool definitions for Okta operations."""

from typing import Any, Dict, List, Optional, Union
from fastmcp import FastMCP

from ..config import Settings
from ..okta.client import OktaClient
from ..utils.logging import get_logger
from ..exceptions import MCPToolError, ValidationError

logger = get_logger(__name__)


def register_tools(mcp: FastMCP, okta_client: OktaClient, settings: Settings) -> None:
    """Register all MCP tools for Okta operations.

    Args:
        mcp: FastMCP server instance
        okta_client: Configured Okta client
        settings: Application settings
    """
    logger.info("Registering MCP tools")

    # User Management Tools
    _register_user_tools(mcp, okta_client)

    # Application Management Tools
    _register_application_tools(mcp, okta_client)

    # System Log Tools
    _register_log_tools(mcp, okta_client)

    logger.info("All MCP tools registered successfully")


def _register_user_tools(mcp: FastMCP, okta_client: OktaClient) -> None:
    """Register user management tools."""

    @mcp.tool()
    async def get_user_details(user_identifier: str) -> Dict[str, Any]:
        """Get detailed information about a user.

        Args:
            user_identifier: User ID, email, or login name

        Returns:
            User details including profile, status, and group memberships
        """
        try:
            logger.info("Getting user details", user_identifier=user_identifier)
            user_data = await okta_client.users.get_user(user_identifier)
            return {
                "success": True,
                "user": user_data,
                "message": f"Successfully retrieved user details for {user_identifier}",
            }
        except Exception as e:
            logger.error("Failed to get user details", error=str(e))
            raise MCPToolError("get_user_details", str(e))

    @mcp.tool()
    async def update_user_profile(
        user_identifier: str, profile_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user profile attributes.

        Args:
            user_identifier: User ID, email, or login name
            profile_updates: Dictionary of profile attributes to update

        Returns:
            Updated user profile information
        """
        try:
            logger.info(
                "Updating user profile",
                user_identifier=user_identifier,
                updates=list(profile_updates.keys()),
            )
            updated_user = await okta_client.users.update_user_profile(
                user_identifier, profile_updates
            )
            return {
                "success": True,
                "user": updated_user,
                "message": f"Successfully updated profile for {user_identifier}",
            }
        except Exception as e:
            logger.error("Failed to update user profile", error=str(e))
            raise MCPToolError("update_user_profile", str(e))

    @mcp.tool()
    async def reinvite_user(user_identifier: str) -> Dict[str, Any]:
        """Re-send invitation email to a user.

        Args:
            user_identifier: User ID, email, or login name

        Returns:
            Result of the re-invitation operation
        """
        try:
            logger.info("Re-inviting user", user_identifier=user_identifier)
            result = await okta_client.users.reactivate_user(user_identifier)
            return {
                "success": True,
                "result": result,
                "message": f"Successfully re-invited user {user_identifier}",
            }
        except Exception as e:
            logger.error("Failed to re-invite user", error=str(e))
            raise MCPToolError("reinvite_user", str(e))

    @mcp.tool()
    async def unlock_user_account(user_identifier: str) -> Dict[str, Any]:
        """Unlock a locked user account.

        Args:
            user_identifier: User ID, email, or login name

        Returns:
            Result of the unlock operation
        """
        try:
            logger.info("Unlocking user account", user_identifier=user_identifier)
            result = await okta_client.users.unlock_user(user_identifier)
            return {
                "success": True,
                "result": result,
                "message": f"Successfully unlocked account for {user_identifier}",
            }
        except Exception as e:
            logger.error("Failed to unlock user account", error=str(e))
            raise MCPToolError("unlock_user_account", str(e))

    @mcp.tool()
    async def reset_user_password(
        user_identifier: str, send_email: bool = True
    ) -> Dict[str, Any]:
        """Reset user password and optionally send reset email.

        Args:
            user_identifier: User ID, email, or login name
            send_email: Whether to send password reset email

        Returns:
            Result of the password reset operation
        """
        try:
            logger.info(
                "Resetting user password",
                user_identifier=user_identifier,
                send_email=send_email,
            )
            result = await okta_client.users.reset_password(user_identifier, send_email)
            return {
                "success": True,
                "result": result,
                "message": f"Successfully initiated password reset for {user_identifier}",
            }
        except Exception as e:
            logger.error("Failed to reset user password", error=str(e))
            raise MCPToolError("reset_user_password", str(e))


def _register_application_tools(mcp: FastMCP, okta_client: OktaClient) -> None:
    """Register application management tools."""

    @mcp.tool()
    async def list_applications(
        limit: int = 20, filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """List applications in the Okta org.

        Args:
            limit: Maximum number of applications to return
            filter_expr: Optional filter expression

        Returns:
            List of applications with basic information
        """
        try:
            logger.info("Listing applications", limit=limit, filter=filter_expr)
            apps = await okta_client.applications.list_applications(limit, filter_expr)
            return {
                "success": True,
                "applications": apps,
                "count": len(apps),
                "message": f"Successfully retrieved {len(apps)} applications",
            }
        except Exception as e:
            logger.error("Failed to list applications", error=str(e))
            raise MCPToolError("list_applications", str(e))

    @mcp.tool()
    async def get_application_details(app_identifier: str) -> Dict[str, Any]:
        """Get detailed information about an application.

        Args:
            app_identifier: Application ID or name

        Returns:
            Detailed application information
        """
        try:
            logger.info("Getting application details", app_identifier=app_identifier)
            app_data = await okta_client.applications.get_application(app_identifier)
            return {
                "success": True,
                "application": app_data,
                "message": f"Successfully retrieved application details for {app_identifier}",
            }
        except Exception as e:
            logger.error("Failed to get application details", error=str(e))
            raise MCPToolError("get_application_details", str(e))

    @mcp.tool()
    async def update_application_config(
        app_identifier: str, config_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update application configuration.

        Args:
            app_identifier: Application ID or name
            config_updates: Dictionary of configuration updates

        Returns:
            Updated application configuration
        """
        try:
            logger.info(
                "Updating application config",
                app_identifier=app_identifier,
                updates=list(config_updates.keys()),
            )
            updated_app = await okta_client.applications.update_application(
                app_identifier, config_updates
            )
            return {
                "success": True,
                "application": updated_app,
                "message": f"Successfully updated configuration for {app_identifier}",
            }
        except Exception as e:
            logger.error("Failed to update application config", error=str(e))
            raise MCPToolError("update_application_config", str(e))


def _register_log_tools(mcp: FastMCP, okta_client: OktaClient) -> None:
    """Register system log tools."""

    @mcp.tool()
    async def get_user_logs(
        user_identifier: str,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get system logs for a specific user.

        Args:
            user_identifier: User ID, email, or login name
            since: ISO timestamp to filter logs since this time
            limit: Maximum number of log entries to return

        Returns:
            User activity logs
        """
        try:
            logger.info(
                "Getting user logs",
                user_identifier=user_identifier,
                since=since,
                limit=limit,
            )
            logs = await okta_client.logs.get_user_logs(user_identifier, since, limit)
            return {
                "success": True,
                "logs": logs,
                "count": len(logs),
                "message": f"Successfully retrieved {len(logs)} log entries for {user_identifier}",
            }
        except Exception as e:
            logger.error("Failed to get user logs", error=str(e))
            raise MCPToolError("get_user_logs", str(e))

    @mcp.tool()
    async def get_application_logs(
        app_identifier: str,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get system logs for a specific application.

        Args:
            app_identifier: Application ID or name
            since: ISO timestamp to filter logs since this time
            limit: Maximum number of log entries to return

        Returns:
            Application activity logs
        """
        try:
            logger.info(
                "Getting application logs",
                app_identifier=app_identifier,
                since=since,
                limit=limit,
            )
            logs = await okta_client.logs.get_application_logs(
                app_identifier, since, limit
            )
            return {
                "success": True,
                "logs": logs,
                "count": len(logs),
                "message": f"Successfully retrieved {len(logs)} log entries for {app_identifier}",
            }
        except Exception as e:
            logger.error("Failed to get application logs", error=str(e))
            raise MCPToolError("get_application_logs", str(e))

    @mcp.tool()
    async def search_logs(
        query: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Search system logs with a query.

        Args:
            query: Search query expression
            since: ISO timestamp to filter logs since this time
            until: ISO timestamp to filter logs until this time
            limit: Maximum number of log entries to return

        Returns:
            Matching log entries
        """
        try:
            logger.info(
                "Searching logs",
                query=query,
                since=since,
                until=until,
                limit=limit,
            )
            logs = await okta_client.logs.search_logs(query, since, until, limit)
            return {
                "success": True,
                "logs": logs,
                "count": len(logs),
                "query": query,
                "message": f"Successfully found {len(logs)} log entries matching query",
            }
        except Exception as e:
            logger.error("Failed to search logs", error=str(e))
            raise MCPToolError("search_logs", str(e))