"""Debug and troubleshooting utilities."""

import os
import sys
import asyncio
import platform
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
import json
from pathlib import Path

from ..config import Settings
from ..exceptions import ConfigurationError
from .logging import get_logger

logger = get_logger(__name__)


class SystemInfo:
    """Collect system information for debugging."""

    @staticmethod
    def get_python_info() -> Dict[str, Any]:
        """Get Python environment information."""
        return {
            "version": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "python_path": sys.path[:5],  # First 5 entries
        }

    @staticmethod
    def get_package_info() -> Dict[str, Any]:
        """Get installed package information."""
        try:
            import pkg_resources
            packages = {}

            # Key packages to check
            key_packages = [
                'fastmcp', 'httpx', 'pydantic', 'pydantic-settings',
                'structlog', 'rich', 'pytest'
            ]

            for package_name in key_packages:
                try:
                    package = pkg_resources.get_distribution(package_name)
                    packages[package_name] = package.version
                except pkg_resources.DistributionNotFound:
                    packages[package_name] = "not installed"

            return packages
        except ImportError:
            return {"error": "pkg_resources not available"}

    @staticmethod
    def get_environment_info() -> Dict[str, Any]:
        """Get environment variable information (sanitized)."""
        env_vars = {}

        # Safe environment variables to include
        safe_vars = [
            'OKTA_ORG_URL', 'MCP_SERVER_NAME', 'MCP_LOG_LEVEL',
            'DEVELOPMENT_MODE', 'LOG_STRUCTURED', 'OKTA_RATE_LIMIT',
            'OKTA_TIMEOUT_SECONDS', 'PYTHON_VERSION', 'PATH'
        ]

        for var in safe_vars:
            value = os.environ.get(var)
            if value:
                # Sanitize sensitive information
                if 'URL' in var and value:
                    # Show domain but hide subdomain details
                    if 'okta.com' in value:
                        env_vars[var] = f"https://[ORG].okta.com"
                    else:
                        env_vars[var] = "[URL_REDACTED]"
                else:
                    env_vars[var] = value
            else:
                env_vars[var] = None

        # Check for presence of sensitive vars without showing values
        sensitive_vars = ['OKTA_API_TOKEN', 'OKTA_CLIENT_SECRET']
        for var in sensitive_vars:
            env_vars[f"{var}_present"] = bool(os.environ.get(var))

        return env_vars

    @staticmethod
    def get_file_system_info() -> Dict[str, Any]:
        """Get file system information."""
        cwd = os.getcwd()
        return {
            "working_directory": cwd,
            "config_files": {
                ".env": os.path.exists(".env"),
                ".env.example": os.path.exists(".env.example"),
                "pyproject.toml": os.path.exists("pyproject.toml"),
                "requirements.txt": os.path.exists("requirements.txt"),
            },
            "directories": {
                "src": os.path.exists("src"),
                "tests": os.path.exists("tests"),
                "docs": os.path.exists("docs"),
                "scripts": os.path.exists("scripts"),
                "venv": os.path.exists("venv"),
            }
        }


class NetworkDiagnostics:
    """Network connectivity diagnostics."""

    @staticmethod
    async def test_dns_resolution(hostname: str) -> Dict[str, Any]:
        """Test DNS resolution for a hostname."""
        import socket

        try:
            start_time = datetime.now()
            ip_address = socket.gethostbyname(hostname)
            end_time = datetime.now()

            return {
                "success": True,
                "ip_address": ip_address,
                "response_time_ms": (end_time - start_time).total_seconds() * 1000,
            }
        except socket.gaierror as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "DNS resolution failed"
            }

    @staticmethod
    async def test_http_connectivity(url: str, timeout: float = 10.0) -> Dict[str, Any]:
        """Test HTTP connectivity to a URL."""
        try:
            start_time = datetime.now()

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)

            end_time = datetime.now()

            return {
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": (end_time - start_time).total_seconds() * 1000,
                "headers": dict(response.headers),
                "content_length": len(response.content),
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timed out",
                "error_type": "timeout"
            }
        except httpx.ConnectError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "connection_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    @staticmethod
    async def test_okta_api_connectivity(settings: Settings) -> Dict[str, Any]:
        """Test Okta API connectivity."""
        results = {}

        # Test basic connectivity
        results["basic_connectivity"] = await NetworkDiagnostics.test_http_connectivity(
            settings.okta_org_url
        )

        # Test API endpoint
        api_url = f"{settings.okta_org_url}/api/v1/users/me"

        try:
            async with httpx.AsyncClient(timeout=settings.okta_timeout_seconds) as client:
                headers = {
                    "Accept": "application/json",
                    "User-Agent": f"mcp-okta-support/{settings.mcp_server_version}",
                }

                if settings.is_api_token_configured:
                    headers["Authorization"] = f"SSWS {settings.okta_api_token}"

                start_time = datetime.now()
                response = await client.get(api_url, headers=headers)
                end_time = datetime.now()

                results["api_connectivity"] = {
                    "success": response.is_success,
                    "status_code": response.status_code,
                    "response_time_ms": (end_time - start_time).total_seconds() * 1000,
                    "auth_method": "api_token" if settings.is_api_token_configured else "oauth",
                }

                if not response.is_success:
                    results["api_connectivity"]["error"] = response.text

        except Exception as e:
            results["api_connectivity"] = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

        return results


class ConfigurationDiagnostics:
    """Configuration validation and diagnostics."""

    @staticmethod
    def validate_configuration() -> Dict[str, Any]:
        """Validate configuration and return diagnostics."""
        results = {
            "config_loading": {"success": False},
            "required_vars": {"success": False},
            "optional_vars": {"success": True, "warnings": []},
            "validation": {"success": False}
        }

        try:
            # Test configuration loading
            settings = Settings()
            results["config_loading"]["success"] = True
            results["config_loading"]["org_url"] = settings.okta_org_url
            results["config_loading"]["auth_method"] = (
                "api_token" if settings.is_api_token_configured else "oauth"
            )

            # Validate required variables
            required_checks = []

            if settings.okta_org_url:
                required_checks.append("OKTA_ORG_URL present")
            else:
                required_checks.append("OKTA_ORG_URL missing")

            if settings.is_api_token_configured:
                required_checks.append("OKTA_API_TOKEN present")
            elif settings.is_oauth_configured:
                required_checks.append("OAuth credentials present")
            else:
                required_checks.append("No authentication method configured")

            results["required_vars"]["checks"] = required_checks
            results["required_vars"]["success"] = all(
                "missing" not in check and "No authentication" not in check
                for check in required_checks
            )

            # Validate optional variables
            if not (1 <= settings.okta_rate_limit <= 1000):
                results["optional_vars"]["warnings"].append(
                    f"Rate limit unusual: {settings.okta_rate_limit}"
                )

            if not (10 <= settings.okta_timeout_seconds <= 300):
                results["optional_vars"]["warnings"].append(
                    f"Timeout unusual: {settings.okta_timeout_seconds}s"
                )

            # Overall validation
            results["validation"]["success"] = (
                results["config_loading"]["success"] and
                results["required_vars"]["success"]
            )

        except Exception as e:
            results["config_loading"]["error"] = str(e)
            results["config_loading"]["error_type"] = type(e).__name__

        return results


class MCPDiagnostics:
    """MCP-specific diagnostics."""

    @staticmethod
    def test_mcp_imports() -> Dict[str, Any]:
        """Test MCP-related imports."""
        results = {}

        # Test core imports
        imports_to_test = [
            'fastmcp',
            'mcp_okta_support',
            'mcp_okta_support.main',
            'mcp_okta_support.config',
            'mcp_okta_support.okta.client',
            'mcp_okta_support.mcp.server',
        ]

        for module_name in imports_to_test:
            try:
                __import__(module_name)
                results[module_name] = {"success": True}
            except ImportError as e:
                results[module_name] = {
                    "success": False,
                    "error": str(e)
                }

        return results

    @staticmethod
    def test_tool_registration() -> Dict[str, Any]:
        """Test MCP tool registration."""
        try:
            from fastmcp import FastMCP
            from mcp_okta_support.config import Settings
            from mcp_okta_support.mcp.server import setup_mcp_server

            # Create test settings
            test_settings = Settings()
            test_settings.okta_org_url = "https://test.okta.com"
            test_settings.okta_api_token = "test_token"

            # Test server setup
            mcp = setup_mcp_server(test_settings)

            return {
                "success": True,
                "server_name": mcp.name if hasattr(mcp, 'name') else "unknown",
                "tools_registered": True,  # If setup_mcp_server succeeds
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }


class DebugReportGenerator:
    """Generate comprehensive debug reports."""

    def __init__(self):
        self.report_data = {}

    async def generate_full_report(self) -> Dict[str, Any]:
        """Generate a comprehensive debug report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": SystemInfo.get_python_info(),
            "packages": SystemInfo.get_package_info(),
            "environment": SystemInfo.get_environment_info(),
            "filesystem": SystemInfo.get_file_system_info(),
            "configuration": ConfigurationDiagnostics.validate_configuration(),
            "mcp_diagnostics": MCPDiagnostics.test_mcp_imports(),
            "tool_registration": MCPDiagnostics.test_tool_registration(),
        }

        # Add network diagnostics if configuration is valid
        if report["configuration"]["config_loading"]["success"]:
            try:
                settings = Settings()

                # Test DNS resolution
                hostname = settings.okta_org_url.replace("https://", "").split("/")[0]
                report["dns_test"] = await NetworkDiagnostics.test_dns_resolution(hostname)

                # Test network connectivity
                report["network_connectivity"] = await NetworkDiagnostics.test_okta_api_connectivity(settings)

            except Exception as e:
                report["network_connectivity"] = {
                    "error": str(e),
                    "error_type": type(e).__name__
                }

        return report

    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save debug report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_report_{timestamp}.json"

        # Create reports directory if it doesn't exist
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        filepath = reports_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return str(filepath)

    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print a summary of the debug report."""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        console.print(Panel.fit(
            "[bold]MCP Okta Support Debug Report Summary[/bold]",
            border_style="blue"
        ))

        # System info summary
        python_version = report["system_info"]["version"].split()[0]
        console.print(f"Python: {python_version}")
        console.print(f"Platform: {report['system_info']['platform']}")

        # Package status
        packages = report["packages"]
        if isinstance(packages, dict):
            missing_packages = [k for k, v in packages.items() if v == "not installed"]
            if missing_packages:
                console.print(f"[red]Missing packages: {', '.join(missing_packages)}[/red]")
            else:
                console.print("[green]All key packages installed[/green]")

        # Configuration status
        config = report["configuration"]
        if config["config_loading"]["success"]:
            console.print("[green]✅ Configuration loaded successfully[/green]")
            auth_method = config["config_loading"].get("auth_method", "unknown")
            console.print(f"Authentication: {auth_method}")
        else:
            console.print("[red]❌ Configuration failed to load[/red]")
            if "error" in config["config_loading"]:
                console.print(f"Error: {config['config_loading']['error']}")

        # Network status
        if "network_connectivity" in report:
            network = report["network_connectivity"]
            if isinstance(network, dict) and "api_connectivity" in network:
                api = network["api_connectivity"]
                if api.get("success"):
                    console.print("[green]✅ Okta API connectivity working[/green]")
                else:
                    console.print("[red]❌ Okta API connectivity failed[/red]")
                    if "error" in api:
                        console.print(f"Error: {api['error']}")

        # MCP status
        mcp_diag = report["mcp_diagnostics"]
        tool_reg = report["tool_registration"]

        failed_imports = [k for k, v in mcp_diag.items() if not v.get("success")]
        if failed_imports:
            console.print(f"[red]❌ Failed imports: {', '.join(failed_imports)}[/red]")
        else:
            console.print("[green]✅ All MCP imports successful[/green]")

        if tool_reg.get("success"):
            console.print("[green]✅ MCP tool registration working[/green]")
        else:
            console.print("[red]❌ MCP tool registration failed[/red]")


async def quick_diagnostic() -> Dict[str, Any]:
    """Run a quick diagnostic check."""
    generator = DebugReportGenerator()

    # Quick checks only
    report = {
        "timestamp": datetime.now().isoformat(),
        "configuration": ConfigurationDiagnostics.validate_configuration(),
        "mcp_imports": MCPDiagnostics.test_mcp_imports(),
    }

    # Test connectivity if config is valid
    if report["configuration"]["config_loading"]["success"]:
        try:
            settings = Settings()
            hostname = settings.okta_org_url.replace("https://", "").split("/")[0]
            report["dns_test"] = await NetworkDiagnostics.test_dns_resolution(hostname)
        except Exception as e:
            report["dns_test"] = {"error": str(e)}

    return report


async def full_diagnostic() -> str:
    """Run full diagnostic and save report."""
    generator = DebugReportGenerator()
    report = await generator.generate_full_report()
    filepath = generator.save_report(report)
    generator.print_summary(report)
    return filepath