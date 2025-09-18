#!/usr/bin/env python3

"""
Configuration validation script for MCP Okta Support.
This script validates your configuration and tests connectivity.
"""

import os
import sys
import asyncio
import argparse
from typing import Dict, Any, List, Optional
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from mcp_okta_support.config import Settings
    from mcp_okta_support.exceptions import ConfigurationError
    from mcp_okta_support.okta.client import OktaClient
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you've installed the package: pip install -e .")
    sys.exit(1)

console = Console()

class ValidationResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors: List[str] = []
        self.warnings_list: List[str] = []

    def pass_test(self, message: str):
        """Mark a test as passed."""
        console.print(f"✅ {message}", style="green")
        self.passed += 1

    def fail_test(self, message: str, error: str = None):
        """Mark a test as failed."""
        console.print(f"❌ {message}", style="red")
        if error:
            console.print(f"   Error: {error}", style="red dim")
            self.errors.append(f"{message}: {error}")
        else:
            self.errors.append(message)
        self.failed += 1

    def warn_test(self, message: str, warning: str = None):
        """Mark a test as warning."""
        console.print(f"⚠️  {message}", style="yellow")
        if warning:
            console.print(f"   Warning: {warning}", style="yellow dim")
            self.warnings_list.append(f"{message}: {warning}")
        else:
            self.warnings_list.append(message)
        self.warnings += 1

    def summary(self) -> bool:
        """Print summary and return True if all tests passed."""
        console.print("\n" + "="*50)
        console.print("VALIDATION SUMMARY", style="bold")
        console.print("="*50)

        # Create summary table
        table = Table()
        table.add_column("Result", style="bold")
        table.add_column("Count", justify="right")

        table.add_row("✅ Passed", str(self.passed), style="green")
        table.add_row("❌ Failed", str(self.failed), style="red")
        table.add_row("⚠️  Warnings", str(self.warnings), style="yellow")

        console.print(table)

        # Show errors if any
        if self.errors:
            console.print("\nErrors:", style="red bold")
            for error in self.errors:
                console.print(f"  • {error}", style="red")

        # Show warnings if any
        if self.warnings_list:
            console.print("\nWarnings:", style="yellow bold")
            for warning in self.warnings_list:
                console.print(f"  • {warning}", style="yellow")

        success = self.failed == 0
        if success:
            console.print("\n🎉 All validations passed!", style="green bold")
        else:
            console.print(f"\n❌ {self.failed} validation(s) failed!", style="red bold")

        return success


async def validate_environment(result: ValidationResult) -> Optional[Settings]:
    """Validate environment configuration."""
    console.print("\n[bold]1. Environment Configuration[/bold]")

    try:
        settings = Settings()
        result.pass_test("Configuration loaded successfully")
        return settings
    except Exception as e:
        result.fail_test("Failed to load configuration", str(e))
        return None


def validate_required_vars(result: ValidationResult, settings: Settings):
    """Validate required environment variables."""
    console.print("\n[bold]2. Required Variables[/bold]")

    # Check Okta org URL
    if settings.okta_org_url:
        if settings.okta_org_url.startswith('https://') and (
            '.okta.com' in settings.okta_org_url or
            '.oktapreview.com' in settings.okta_org_url
        ):
            result.pass_test(f"OKTA_ORG_URL format valid: {settings.okta_org_url}")
        else:
            result.warn_test("OKTA_ORG_URL format unusual",
                           f"Expected https://your-org.okta.com, got {settings.okta_org_url}")
    else:
        result.fail_test("OKTA_ORG_URL is required")

    # Check authentication method
    if settings.is_api_token_configured:
        if len(settings.okta_api_token) > 30:
            result.pass_test("OKTA_API_TOKEN is configured")
        else:
            result.warn_test("OKTA_API_TOKEN seems too short",
                           "API tokens are typically 40+ characters")
    elif settings.is_oauth_configured:
        result.pass_test("OAuth 2.0 credentials configured")

        # Validate scopes
        required_scopes = {'okta.users.manage', 'okta.apps.manage', 'okta.logs.read'}
        user_scopes = set(settings.okta_scopes)
        missing_scopes = required_scopes - user_scopes

        if not missing_scopes:
            result.pass_test("All required OAuth scopes configured")
        else:
            result.warn_test("Some recommended scopes missing",
                           f"Missing: {', '.join(missing_scopes)}")
    else:
        result.fail_test("No authentication method configured",
                        "Set either OKTA_API_TOKEN or OKTA_CLIENT_ID+OKTA_CLIENT_SECRET")


def validate_optional_vars(result: ValidationResult, settings: Settings):
    """Validate optional configuration variables."""
    console.print("\n[bold]3. Optional Configuration[/bold]")

    # Check rate limit
    if 1 <= settings.okta_rate_limit <= 1000:
        result.pass_test(f"Rate limit reasonable: {settings.okta_rate_limit} req/min")
    else:
        result.warn_test("Rate limit seems unusual",
                        f"Got {settings.okta_rate_limit}, typically 50-500")

    # Check timeout
    if 10 <= settings.okta_timeout_seconds <= 300:
        result.pass_test(f"Timeout reasonable: {settings.okta_timeout_seconds}s")
    else:
        result.warn_test("Timeout seems unusual",
                        f"Got {settings.okta_timeout_seconds}s, typically 30-120s")

    # Check log level
    valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    if settings.mcp_log_level in valid_levels:
        result.pass_test(f"Log level valid: {settings.mcp_log_level}")
    else:
        result.fail_test("Invalid log level",
                        f"Got {settings.mcp_log_level}, must be one of {valid_levels}")


async def test_network_connectivity(result: ValidationResult, settings: Settings):
    """Test network connectivity to Okta."""
    console.print("\n[bold]4. Network Connectivity[/bold]")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test basic connectivity
            response = await client.get(settings.okta_org_url)
            if response.status_code < 500:
                result.pass_test("Okta organization reachable")
            else:
                result.fail_test("Okta organization unreachable",
                               f"HTTP {response.status_code}")
    except httpx.TimeoutException:
        result.fail_test("Connection timeout", "Check network connectivity")
    except httpx.ConnectError:
        result.fail_test("Connection failed", "Check URL and network settings")
    except Exception as e:
        result.fail_test("Network test failed", str(e))


async def test_api_authentication(result: ValidationResult, settings: Settings):
    """Test API authentication."""
    console.print("\n[bold]5. API Authentication[/bold]")

    try:
        async with OktaClient(settings) as client:
            # Test with /users/me endpoint (minimal permissions required)
            response = await client.request("GET", "/users/me")
            if response:
                result.pass_test("API authentication successful")

                # Show authenticated user info
                user_login = response.get('profile', {}).get('login', 'Unknown')
                console.print(f"   Authenticated as: {user_login}", style="dim")
            else:
                result.fail_test("API authentication failed", "Empty response")

    except Exception as e:
        result.fail_test("API authentication failed", str(e))


async def test_api_permissions(result: ValidationResult, settings: Settings):
    """Test API permissions for required operations."""
    console.print("\n[bold]6. API Permissions[/bold]")

    try:
        async with OktaClient(settings) as client:
            # Test user read permissions
            try:
                await client.request("GET", "/users", params={"limit": "1"})
                result.pass_test("User read permissions available")
            except Exception as e:
                result.warn_test("User read permissions limited", str(e))

            # Test app read permissions
            try:
                await client.request("GET", "/apps", params={"limit": "1"})
                result.pass_test("Application read permissions available")
            except Exception as e:
                result.warn_test("Application read permissions limited", str(e))

            # Test logs read permissions
            try:
                await client.request("GET", "/logs", params={"limit": "1"})
                result.pass_test("System logs read permissions available")
            except Exception as e:
                result.warn_test("System logs read permissions limited", str(e))

    except Exception as e:
        result.fail_test("Permission test failed", str(e))


def validate_mcp_integration(result: ValidationResult):
    """Validate MCP integration readiness."""
    console.print("\n[bold]7. MCP Integration[/bold]")

    try:
        # Check FastMCP import
        import fastmcp
        result.pass_test("FastMCP library available")

        # Check if main module can be imported
        from mcp_okta_support.main import main
        result.pass_test("MCP server module importable")

        # Check tool registration
        from mcp_okta_support.mcp.tools import register_tools
        from mcp_okta_support.mcp.resources import register_resources
        result.pass_test("MCP tools and resources available")

    except ImportError as e:
        result.fail_test("MCP integration not ready", str(e))


def show_configuration_summary(settings: Settings):
    """Show current configuration summary."""
    console.print("\n[bold]Configuration Summary[/bold]")

    # Create configuration table
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="bold")
    table.add_column("Value")

    table.add_row("Okta Org URL", settings.okta_org_url)
    table.add_row("Authentication",
                  "API Token" if settings.is_api_token_configured else "OAuth 2.0")
    table.add_row("Server Name", settings.mcp_server_name)
    table.add_row("Log Level", settings.mcp_log_level)
    table.add_row("Rate Limit", f"{settings.okta_rate_limit} req/min")
    table.add_row("Timeout", f"{settings.okta_timeout_seconds}s")
    table.add_row("Development Mode", str(settings.development_mode))

    if settings.is_oauth_configured:
        table.add_row("OAuth Scopes", ", ".join(settings.okta_scopes))

    console.print(table)


async def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate MCP Okta Support configuration")
    parser.add_argument("--config", "-c", default=".env",
                       help="Configuration file path (default: .env)")
    parser.add_argument("--quick", "-q", action="store_true",
                       help="Skip network tests (quick validation)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    # Set environment file if specified
    if args.config != ".env":
        os.environ.setdefault("ENV_FILE", args.config)

    console.print(Panel.fit(
        "[bold]MCP Okta Support Configuration Validator[/bold]\n"
        "This tool validates your configuration and tests connectivity.",
        title="🔍 Validator",
        border_style="blue"
    ))

    result = ValidationResult()

    # Load and validate configuration
    settings = await validate_environment(result)
    if not settings:
        result.summary()
        return sys.exit(1)

    # Show current configuration
    if args.verbose:
        show_configuration_summary(settings)

    # Run validations
    validate_required_vars(result, settings)
    validate_optional_vars(result, settings)

    if not args.quick:
        await test_network_connectivity(result, settings)
        await test_api_authentication(result, settings)
        await test_api_permissions(result, settings)

    validate_mcp_integration(result)

    # Show summary
    success = result.summary()

    if success:
        console.print("\n[green]✅ Your configuration is ready! You can start the MCP server with:[/green]")
        console.print("[green]   python -m mcp_okta_support.main[/green]")
    else:
        console.print("\n[red]❌ Please fix the configuration issues above before starting the server.[/red]")

    return sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())