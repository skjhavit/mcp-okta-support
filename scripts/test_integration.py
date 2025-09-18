#!/usr/bin/env python3

"""
Integration test script for MCP Okta Support.
Tests the MCP server with simulated client requests.
"""

import os
import sys
import asyncio
import argparse
import json
from datetime import datetime
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from mcp_okta_support.config import Settings
    from mcp_okta_support.mcp.server import setup_mcp_server
    from mcp_okta_support.okta.client import OktaClient
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you've installed the package: pip install -e .")
    sys.exit(1)

console = Console()


class MCPIntegrationTester:
    """Integration tester for MCP Okta Support."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.mcp_server = None
        self.okta_client = None
        self.test_results = []

    async def setup(self):
        """Set up test environment."""
        console.print("🔧 Setting up test environment...")

        try:
            # Initialize MCP server
            self.mcp_server = setup_mcp_server(self.settings)
            console.print("✅ MCP server initialized")

            # Initialize Okta client
            self.okta_client = OktaClient(self.settings)
            console.print("✅ Okta client initialized")

        except Exception as e:
            console.print(f"❌ Setup failed: {e}")
            raise

    async def teardown(self):
        """Clean up test environment."""
        if self.okta_client:
            await self.okta_client.close()

    async def test_basic_connectivity(self) -> Dict[str, Any]:
        """Test basic Okta API connectivity."""
        test_name = "Basic Connectivity"
        console.print(f"🔍 Testing {test_name}...")

        try:
            # Test /users/me endpoint
            response = await self.okta_client.request("GET", "/users/me")

            if response and "profile" in response:
                return {
                    "test": test_name,
                    "success": True,
                    "message": f"Connected as {response['profile'].get('login', 'unknown')}",
                    "response_size": len(str(response))
                }
            else:
                return {
                    "test": test_name,
                    "success": False,
                    "message": "Empty or invalid response"
                }

        except Exception as e:
            return {
                "test": test_name,
                "success": False,
                "message": str(e),
                "error_type": type(e).__name__
            }

    async def test_user_operations(self) -> List[Dict[str, Any]]:
        """Test user management operations."""
        results = []

        # Test 1: List users
        test_name = "List Users"
        console.print(f"🔍 Testing {test_name}...")

        try:
            users = await self.okta_client.users.list_users(limit=5)

            if users and len(users) > 0:
                results.append({
                    "test": test_name,
                    "success": True,
                    "message": f"Retrieved {len(users)} users",
                    "user_count": len(users)
                })

                # Test 2: Get specific user details (use first user)
                first_user = users[0]
                user_id = first_user.get('id')

                if user_id:
                    test_name = "Get User Details"
                    console.print(f"🔍 Testing {test_name}...")

                    try:
                        user_details = await self.okta_client.users.get_user(user_id)
                        results.append({
                            "test": test_name,
                            "success": True,
                            "message": f"Retrieved details for user {user_id}",
                            "user_status": user_details.get('status', 'unknown')
                        })
                    except Exception as e:
                        results.append({
                            "test": test_name,
                            "success": False,
                            "message": str(e),
                            "error_type": type(e).__name__
                        })

            else:
                results.append({
                    "test": test_name,
                    "success": False,
                    "message": "No users returned or empty response"
                })

        except Exception as e:
            results.append({
                "test": test_name,
                "success": False,
                "message": str(e),
                "error_type": type(e).__name__
            })

        return results

    async def test_application_operations(self) -> List[Dict[str, Any]]:
        """Test application management operations."""
        results = []

        # Test 1: List applications
        test_name = "List Applications"
        console.print(f"🔍 Testing {test_name}...")

        try:
            apps = await self.okta_client.applications.list_applications(limit=5)

            if apps and len(apps) > 0:
                results.append({
                    "test": test_name,
                    "success": True,
                    "message": f"Retrieved {len(apps)} applications",
                    "app_count": len(apps)
                })

                # Test 2: Get specific application details
                first_app = apps[0]
                app_id = first_app.get('id')

                if app_id:
                    test_name = "Get Application Details"
                    console.print(f"🔍 Testing {test_name}...")

                    try:
                        app_details = await self.okta_client.applications.get_application(app_id)
                        results.append({
                            "test": test_name,
                            "success": True,
                            "message": f"Retrieved details for app {app_id}",
                            "app_status": app_details.get('status', 'unknown')
                        })
                    except Exception as e:
                        results.append({
                            "test": test_name,
                            "success": False,
                            "message": str(e),
                            "error_type": type(e).__name__
                        })

            else:
                results.append({
                    "test": test_name,
                    "success": False,
                    "message": "No applications returned or empty response"
                })

        except Exception as e:
            results.append({
                "test": test_name,
                "success": False,
                "message": str(e),
                "error_type": type(e).__name__
            })

        return results

    async def test_log_operations(self) -> List[Dict[str, Any]]:
        """Test system log operations."""
        results = []

        # Test 1: Get recent logs
        test_name = "Get System Logs"
        console.print(f"🔍 Testing {test_name}...")

        try:
            logs = await self.okta_client.logs.get_logs(limit=10)

            if logs and len(logs) > 0:
                results.append({
                    "test": test_name,
                    "success": True,
                    "message": f"Retrieved {len(logs)} log entries",
                    "log_count": len(logs)
                })

                # Test 2: Search logs with filter
                test_name = "Search Logs"
                console.print(f"🔍 Testing {test_name}...")

                try:
                    # Search for authentication events
                    auth_logs = await self.okta_client.logs.search_logs(
                        "eventType sw \"user.session\"",
                        limit=5
                    )
                    results.append({
                        "test": test_name,
                        "success": True,
                        "message": f"Found {len(auth_logs)} authentication events",
                        "search_results": len(auth_logs)
                    })
                except Exception as e:
                    results.append({
                        "test": test_name,
                        "success": False,
                        "message": str(e),
                        "error_type": type(e).__name__
                    })

            else:
                results.append({
                    "test": test_name,
                    "success": False,
                    "message": "No logs returned or empty response"
                })

        except Exception as e:
            results.append({
                "test": test_name,
                "success": False,
                "message": str(e),
                "error_type": type(e).__name__
            })

        return results

    async def test_error_handling(self) -> List[Dict[str, Any]]:
        """Test error handling scenarios."""
        results = []

        # Test 1: Invalid user ID
        test_name = "Error Handling - Invalid User"
        console.print(f"🔍 Testing {test_name}...")

        try:
            await self.okta_client.users.get_user("invalid_user_id_12345")
            results.append({
                "test": test_name,
                "success": False,
                "message": "Expected error but operation succeeded"
            })
        except Exception as e:
            # This should fail, which is the expected behavior
            results.append({
                "test": test_name,
                "success": True,
                "message": f"Correctly handled error: {type(e).__name__}",
                "error_handled": type(e).__name__
            })

        # Test 2: Invalid application ID
        test_name = "Error Handling - Invalid Application"
        console.print(f"🔍 Testing {test_name}...")

        try:
            await self.okta_client.applications.get_application("invalid_app_id_12345")
            results.append({
                "test": test_name,
                "success": False,
                "message": "Expected error but operation succeeded"
            })
        except Exception as e:
            # This should fail, which is the expected behavior
            results.append({
                "test": test_name,
                "success": True,
                "message": f"Correctly handled error: {type(e).__name__}",
                "error_handled": type(e).__name__
            })

        return results

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        start_time = datetime.now()
        all_results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running integration tests...", total=None)

            # Basic connectivity
            result = await self.test_basic_connectivity()
            all_results.append(result)

            # User operations
            user_results = await self.test_user_operations()
            all_results.extend(user_results)

            # Application operations
            app_results = await self.test_application_operations()
            all_results.extend(app_results)

            # Log operations
            log_results = await self.test_log_operations()
            all_results.extend(log_results)

            # Error handling
            error_results = await self.test_error_handling()
            all_results.extend(error_results)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Compile summary
        passed = sum(1 for r in all_results if r.get("success"))
        failed = len(all_results) - passed

        return {
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": len(all_results),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(all_results)) * 100 if all_results else 0,
            "results": all_results
        }

    def print_summary(self, report: Dict[str, Any]):
        """Print test summary."""
        console.print("\n" + "="*60)
        console.print("INTEGRATION TEST SUMMARY", style="bold")
        console.print("="*60)

        # Overall stats
        total = report["total_tests"]
        passed = report["passed"]
        failed = report["failed"]
        success_rate = report["success_rate"]

        stats_table = Table()
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value")

        stats_table.add_row("Total Tests", str(total))
        stats_table.add_row("Passed", f"[green]{passed}[/green]")
        stats_table.add_row("Failed", f"[red]{failed}[/red]")
        stats_table.add_row("Success Rate", f"{success_rate:.1f}%")
        stats_table.add_row("Duration", f"{report['duration_seconds']:.2f}s")

        console.print(stats_table)

        # Detailed results
        console.print("\nDetailed Results:")
        results_table = Table()
        results_table.add_column("Test")
        results_table.add_column("Status")
        results_table.add_column("Message")

        for result in report["results"]:
            test_name = result["test"]
            success = result["success"]
            message = result["message"]

            status = "[green]✅ PASS[/green]" if success else "[red]❌ FAIL[/red]"
            results_table.add_row(test_name, status, message)

        console.print(results_table)

        # Overall result
        if failed == 0:
            console.print("\n🎉 [green]All tests passed![/green]")
        else:
            console.print(f"\n❌ [red]{failed} test(s) failed[/red]")
            console.print("Check the detailed results above for more information.")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="MCP Okta Support Integration Tester")
    parser.add_argument("--config", "-c", default=".env",
                       help="Configuration file path (default: .env)")
    parser.add_argument("--save-report", "-s", action="store_true",
                       help="Save test report to file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    # Set environment file if specified
    if args.config != ".env":
        os.environ.setdefault("ENV_FILE", args.config)

    console.print(Panel.fit(
        "[bold]MCP Okta Support Integration Tester[/bold]\n"
        "This tool tests the complete MCP server functionality.",
        title="🧪 Integration Tester",
        border_style="green"
    ))

    try:
        # Load configuration
        settings = Settings()
        console.print("✅ Configuration loaded successfully")

        # Initialize tester
        tester = MCPIntegrationTester(settings)

        # Setup
        await tester.setup()

        # Run tests
        console.print("\n🚀 Starting integration tests...\n")
        report = await tester.run_all_tests()

        # Print summary
        tester.print_summary(report)

        # Save report if requested
        if args.save_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integration_test_report_{timestamp}.json"

            os.makedirs("reports", exist_ok=True)
            filepath = os.path.join("reports", filename)

            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            console.print(f"\n📄 Report saved to: [blue]{filepath}[/blue]")

        # Cleanup
        await tester.teardown()

        # Exit code based on test results
        exit_code = 0 if report["failed"] == 0 else 1
        sys.exit(exit_code)

    except Exception as e:
        console.print(f"\n❌ Integration test failed: {e}")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n⏹️  Test interrupted by user")
        sys.exit(1)