"""MCP resource definitions for Okta data exposure."""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

from ..config import Settings
from ..okta.client import OktaClient
from ..utils.logging import get_logger

logger = get_logger(__name__)


def register_resources(mcp: FastMCP, okta_client: OktaClient, settings: Settings) -> None:
    """Register MCP resources for data exposure.

    Args:
        mcp: FastMCP server instance
        okta_client: Configured Okta client
        settings: Application settings
    """
    logger.info("Registering MCP resources")

    # Organization information
    @mcp.resource("okta://org/info")
    def get_org_info() -> Dict[str, Any]:
        """Get Okta organization information."""
        return {
            "org_url": settings.okta_org_url,
            "server_name": settings.mcp_server_name,
            "server_version": settings.mcp_server_version,
            "authentication_type": "oauth" if settings.is_oauth_configured else "api_token",
            "supported_operations": [
                "user_management",
                "application_management",
                "system_logs",
            ],
        }

    # User templates and examples
    @mcp.resource("okta://templates/user_update")
    def get_user_update_template() -> Dict[str, Any]:
        """Get template for user profile updates."""
        return {
            "description": "Template for updating user profile attributes",
            "example": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@company.com",
                "title": "Software Engineer",
                "department": "Engineering",
                "manager": "jane.smith@company.com",
                "customAttributes": {
                    "employeeId": "E12345",
                    "costCenter": "CC001",
                },
            },
            "supported_attributes": [
                "firstName",
                "lastName",
                "email",
                "title",
                "department",
                "manager",
                "mobilePhone",
                "city",
                "state",
                "zipCode",
                "countryCode",
            ],
        }

    # Application configuration templates
    @mcp.resource("okta://templates/application_config")
    def get_app_config_template() -> Dict[str, Any]:
        """Get template for application configuration updates."""
        return {
            "description": "Template for updating application configuration",
            "example": {
                "label": "My Application",
                "settings": {
                    "app": {
                        "baseUrl": "https://myapp.company.com",
                        "autoSubmitToolbar": False,
                        "hideIOS": False,
                        "hideWeb": False,
                    },
                    "signOn": {
                        "defaultRelayState": "",
                        "ssoAcsUrl": "https://myapp.company.com/sso/saml",
                        "idpIssuer": "http://www.okta.com/${org.externalKey}",
                        "audience": "https://myapp.company.com",
                    },
                },
            },
            "configurable_settings": [
                "label",
                "visibility",
                "settings.app",
                "settings.signOn",
                "features",
            ],
        }

    # Log search examples
    @mcp.resource("okta://examples/log_queries")
    def get_log_query_examples() -> Dict[str, Any]:
        """Get examples of log search queries."""
        return {
            "description": "Common log search query examples",
            "examples": {
                "failed_logins": {
                    "query": "eventType eq \"user.session.start\" and outcome.result eq \"FAILURE\"",
                    "description": "Find failed login attempts",
                },
                "password_resets": {
                    "query": "eventType eq \"user.account.reset_password\"",
                    "description": "Find password reset events",
                },
                "app_assignments": {
                    "query": "eventType eq \"application.user_membership.add\"",
                    "description": "Find application assignment events",
                },
                "user_creations": {
                    "query": "eventType eq \"user.lifecycle.create\"",
                    "description": "Find user creation events",
                },
                "admin_actions": {
                    "query": "actor.type eq \"User\" and actor.alternateId eq \"admin@company.com\"",
                    "description": "Find actions by specific admin user",
                },
                "suspicious_activity": {
                    "query": "severity eq \"WARN\" or severity eq \"ERROR\"",
                    "description": "Find warning and error events",
                },
            },
            "supported_filters": [
                "eventType",
                "outcome.result",
                "actor.alternateId",
                "target.alternateId",
                "severity",
                "published",
            ],
        }

    # Help and usage information
    @mcp.resource("okta://help/usage")
    def get_usage_help() -> Dict[str, Any]:
        """Get usage help and command examples."""
        return {
            "description": "Usage help and examples for MCP Okta Support tools",
            "user_management": {
                "get_user_details": {
                    "description": "Get detailed information about a user",
                    "examples": [
                        "Get details for user john.doe@company.com",
                        "Show me information about user ID 00u1a2b3c4d5e6f7",
                        "What are the details for user johndoe?",
                    ],
                },
                "update_user_profile": {
                    "description": "Update user profile attributes",
                    "examples": [
                        "Update user john.doe@company.com's title to 'Senior Engineer'",
                        "Change the department for user ID 00u1a2b3c4d5e6f7 to 'Marketing'",
                        "Update user johndoe's manager to jane.smith@company.com",
                    ],
                },
                "unlock_user_account": {
                    "description": "Unlock a locked user account",
                    "examples": [
                        "Unlock account for user john.doe@company.com",
                        "Unlock user ID 00u1a2b3c4d5e6f7",
                    ],
                },
                "reset_user_password": {
                    "description": "Reset user password",
                    "examples": [
                        "Reset password for user john.doe@company.com",
                        "Send password reset email to user ID 00u1a2b3c4d5e6f7",
                    ],
                },
            },
            "application_management": {
                "list_applications": {
                    "description": "List applications in the organization",
                    "examples": [
                        "Show me all applications",
                        "List the first 10 applications",
                        "Show applications with 'SAML' in the name",
                    ],
                },
                "get_application_details": {
                    "description": "Get detailed application information",
                    "examples": [
                        "Get details for application 'My App'",
                        "Show me information about app ID 0oa1b2c3d4e5f6g7",
                    ],
                },
            },
            "system_logs": {
                "get_user_logs": {
                    "description": "Get activity logs for a specific user",
                    "examples": [
                        "Show logs for user john.doe@company.com from the last 24 hours",
                        "Get recent activity for user ID 00u1a2b3c4d5e6f7",
                    ],
                },
                "search_logs": {
                    "description": "Search system logs with queries",
                    "examples": [
                        "Find all failed login attempts",
                        "Show password reset events from last week",
                        "Search for admin actions by jane.smith@company.com",
                    ],
                },
            },
        }

    # System prompt resource
    @mcp.resource("okta://prompts/system")
    def get_system_prompt_resource() -> Dict[str, Any]:
        """Get the system prompt for the Okta Support Agent."""
        try:
            from .prompts import get_system_prompt
            return {
                "description": "Comprehensive system prompt for Okta Support Agent",
                "content": get_system_prompt(),
                "usage": "Use this prompt to configure your LLM as an expert Okta troubleshooter",
                "version": "1.0"
            }
        except Exception as e:
            return {
                "description": "System prompt (error loading)",
                "error": str(e),
                "fallback": "You are an expert Okta Support Agent. Help users troubleshoot issues systematically."
            }

    # Troubleshooting workflows
    @mcp.resource("okta://workflows/troubleshooting")
    def get_troubleshooting_workflows() -> Dict[str, Any]:
        """Get structured troubleshooting workflows."""
        try:
            from .prompts import get_troubleshooting_workflows
            return {
                "description": "Structured workflows for common Okta issues",
                "workflows": get_troubleshooting_workflows(),
                "usage": "Follow these workflows for systematic issue resolution"
            }
        except Exception as e:
            return {"error": str(e)}

    # Response templates
    @mcp.resource("okta://templates/responses")
    def get_response_templates() -> Dict[str, Any]:
        """Get response templates for common scenarios."""
        try:
            from .prompts import get_response_templates
            return {
                "description": "Response templates for common support scenarios",
                "templates": get_response_templates(),
                "usage": "Use these templates to provide consistent, helpful responses"
            }
        except Exception as e:
            return {"error": str(e)}

    logger.info("MCP resources registered successfully")