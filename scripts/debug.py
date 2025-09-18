#!/usr/bin/env python3

"""
Debug tool for MCP Okta Support.
Run diagnostics and troubleshooting checks.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from mcp_okta_support.utils.debug import (
        DebugReportGenerator,
        quick_diagnostic,
        full_diagnostic,
        SystemInfo,
        NetworkDiagnostics,
        ConfigurationDiagnostics,
        MCPDiagnostics
    )
    from mcp_okta_support.config import Settings
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you've installed the package: pip install -e .")
    sys.exit(1)

console = Console()


async def cmd_quick():
    """Run quick diagnostic checks."""
    console.print("🔍 Running quick diagnostics...\n")

    report = await quick_diagnostic()

    # Configuration status
    config = report["configuration"]
    if config["config_loading"]["success"]:
        console.print("✅ Configuration: [green]OK[/green]")
    else:
        console.print("❌ Configuration: [red]FAILED[/red]")
        if "error" in config["config_loading"]:
            console.print(f"   Error: {config['config_loading']['error']}")

    # Import status
    imports = report["mcp_imports"]
    failed_imports = [k for k, v in imports.items() if not v.get("success")]
    if failed_imports:
        console.print(f"❌ Imports: [red]FAILED[/red] ({len(failed_imports)} modules)")
        for module in failed_imports:
            console.print(f"   • {module}: {imports[module].get('error', 'unknown error')}")
    else:
        console.print("✅ Imports: [green]OK[/green]")

    # DNS test
    if "dns_test" in report:
        dns = report["dns_test"]
        if dns.get("success"):
            console.print("✅ DNS Resolution: [green]OK[/green]")
        else:
            console.print("❌ DNS Resolution: [red]FAILED[/red]")
            console.print(f"   Error: {dns.get('error', 'unknown')}")

    console.print("\n💡 For detailed diagnostics, run: python scripts/debug.py full")


async def cmd_full():
    """Run full diagnostic report."""
    console.print("🔍 Running full diagnostics (this may take a moment)...\n")

    filepath = await full_diagnostic()

    console.print(f"\n📄 Full report saved to: [blue]{filepath}[/blue]")
    console.print("💡 Share this file when reporting issues")


async def cmd_config():
    """Check configuration only."""
    console.print("⚙️  Checking configuration...\n")

    results = ConfigurationDiagnostics.validate_configuration()

    # Config loading
    if results["config_loading"]["success"]:
        console.print("✅ Configuration loading: [green]OK[/green]")

        org_url = results["config_loading"].get("org_url", "unknown")
        auth_method = results["config_loading"].get("auth_method", "unknown")

        console.print(f"   Org URL: {org_url}")
        console.print(f"   Auth method: {auth_method}")
    else:
        console.print("❌ Configuration loading: [red]FAILED[/red]")
        error = results["config_loading"].get("error", "unknown error")
        console.print(f"   Error: {error}")
        return

    # Required variables
    if results["required_vars"]["success"]:
        console.print("✅ Required variables: [green]OK[/green]")
    else:
        console.print("❌ Required variables: [red]MISSING[/red]")
        for check in results["required_vars"]["checks"]:
            if "missing" in check or "No authentication" in check:
                console.print(f"   ❌ {check}")
            else:
                console.print(f"   ✅ {check}")

    # Optional variables warnings
    warnings = results["optional_vars"]["warnings"]
    if warnings:
        console.print("⚠️  Optional variable warnings:")
        for warning in warnings:
            console.print(f"   • {warning}")


async def cmd_network():
    """Test network connectivity."""
    console.print("🌐 Testing network connectivity...\n")

    try:
        settings = Settings()
    except Exception as e:
        console.print(f"❌ Cannot load configuration: {e}")
        return

    # Extract hostname from URL
    hostname = settings.okta_org_url.replace("https://", "").split("/")[0]

    # DNS test
    console.print(f"🔍 Testing DNS resolution for {hostname}...")
    dns_result = await NetworkDiagnostics.test_dns_resolution(hostname)

    if dns_result["success"]:
        console.print(f"✅ DNS: [green]OK[/green] ({dns_result['ip_address']})")
        console.print(f"   Response time: {dns_result['response_time_ms']:.1f}ms")
    else:
        console.print(f"❌ DNS: [red]FAILED[/red]")
        console.print(f"   Error: {dns_result['error']}")
        return

    # HTTP connectivity test
    console.print(f"🔍 Testing HTTP connectivity to {settings.okta_org_url}...")
    http_result = await NetworkDiagnostics.test_http_connectivity(settings.okta_org_url)

    if http_result["success"]:
        console.print(f"✅ HTTP: [green]OK[/green] (status {http_result['status_code']})")
        console.print(f"   Response time: {http_result['response_time_ms']:.1f}ms")
    else:
        console.print(f"❌ HTTP: [red]FAILED[/red]")
        console.print(f"   Error: {http_result['error']}")
        return

    # API connectivity test
    console.print("🔍 Testing Okta API connectivity...")
    api_results = await NetworkDiagnostics.test_okta_api_connectivity(settings)

    if "api_connectivity" in api_results:
        api = api_results["api_connectivity"]
        if api["success"]:
            console.print(f"✅ API: [green]OK[/green] (status {api['status_code']})")
            console.print(f"   Auth method: {api['auth_method']}")
            console.print(f"   Response time: {api['response_time_ms']:.1f}ms")
        else:
            console.print(f"❌ API: [red]FAILED[/red] (status {api.get('status_code', 'unknown')})")
            if "error" in api:
                console.print(f"   Error: {api['error']}")


async def cmd_mcp():
    """Test MCP components."""
    console.print("🔌 Testing MCP components...\n")

    # Test imports
    console.print("🔍 Testing imports...")
    import_results = MCPDiagnostics.test_mcp_imports()

    for module, result in import_results.items():
        if result["success"]:
            console.print(f"✅ {module}")
        else:
            console.print(f"❌ {module}: [red]{result['error']}[/red]")

    # Test tool registration
    console.print("\n🔍 Testing tool registration...")
    tool_result = MCPDiagnostics.test_tool_registration()

    if tool_result["success"]:
        console.print("✅ Tool registration: [green]OK[/green]")
        if "server_name" in tool_result:
            console.print(f"   Server name: {tool_result['server_name']}")
    else:
        console.print("❌ Tool registration: [red]FAILED[/red]")
        console.print(f"   Error: {tool_result['error']}")


def cmd_system():
    """Show system information."""
    console.print("💻 System Information\n")

    # Python info
    python_info = SystemInfo.get_python_info()
    console.print(f"Python version: {python_info['version'].split()[0]}")
    console.print(f"Python executable: {python_info['executable']}")
    console.print(f"Platform: {python_info['platform']}")

    # Package info
    console.print("\n📦 Package Information")
    package_info = SystemInfo.get_package_info()

    if isinstance(package_info, dict) and "error" not in package_info:
        table = Table()
        table.add_column("Package")
        table.add_column("Version")

        for package, version in package_info.items():
            if version == "not installed":
                table.add_row(package, "[red]not installed[/red]")
            else:
                table.add_row(package, f"[green]{version}[/green]")

        console.print(table)
    else:
        console.print("❌ Could not retrieve package information")

    # Environment info
    console.print("\n🌍 Environment")
    env_info = SystemInfo.get_environment_info()

    for var, value in env_info.items():
        if value is None:
            console.print(f"{var}: [dim]not set[/dim]")
        elif isinstance(value, bool):
            status = "[green]yes[/green]" if value else "[red]no[/red]"
            console.print(f"{var}: {status}")
        else:
            console.print(f"{var}: {value}")

    # File system info
    console.print("\n📁 File System")
    fs_info = SystemInfo.get_file_system_info()

    console.print(f"Working directory: {fs_info['working_directory']}")

    console.print("\nConfig files:")
    for file, exists in fs_info['config_files'].items():
        status = "[green]✓[/green]" if exists else "[red]✗[/red]"
        console.print(f"  {file}: {status}")

    console.print("\nDirectories:")
    for dir_name, exists in fs_info['directories'].items():
        status = "[green]✓[/green]" if exists else "[red]✗[/red]"
        console.print(f"  {dir_name}/: {status}")


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="MCP Okta Support Debug Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Quick diagnostic
    quick_parser = subparsers.add_parser("quick", help="Run quick diagnostic checks")

    # Full diagnostic
    full_parser = subparsers.add_parser("full", help="Generate full diagnostic report")

    # Configuration check
    config_parser = subparsers.add_parser("config", help="Check configuration only")

    # Network test
    network_parser = subparsers.add_parser("network", help="Test network connectivity")

    # MCP test
    mcp_parser = subparsers.add_parser("mcp", help="Test MCP components")

    # System info
    system_parser = subparsers.add_parser("system", help="Show system information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Header
    console.print(Panel.fit(
        "[bold]MCP Okta Support Debug Tool[/bold]",
        border_style="blue"
    ))

    # Route to appropriate command
    if args.command == "quick":
        await cmd_quick()
    elif args.command == "full":
        await cmd_full()
    elif args.command == "config":
        await cmd_config()
    elif args.command == "network":
        await cmd_network()
    elif args.command == "mcp":
        await cmd_mcp()
    elif args.command == "system":
        cmd_system()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n⏹️  Interrupted by user")
    except Exception as e:
        console.print(f"\n❌ Error: {e}")
        sys.exit(1)