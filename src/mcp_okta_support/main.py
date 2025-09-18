#!/usr/bin/env python3

import asyncio
import sys
from typing import Optional

from fastmcp import FastMCP
from pydantic import ValidationError

from .config import Settings
from .mcp.server import setup_mcp_server
from .utils.logging import setup_logging


async def main() -> None:
    """Main entry point for the MCP Okta Support server."""
    try:
        settings = Settings()
    except ValidationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    setup_logging(settings.log_level, settings.log_structured)

    mcp = setup_mcp_server(settings)

    if settings.development_mode:
        print(f"Starting MCP Okta Support server in development mode")
        print(f"Okta org: {settings.okta_org_url}")
        print(f"Log level: {settings.log_level}")

    await mcp.run()


def cli_main() -> None:
    """CLI entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()