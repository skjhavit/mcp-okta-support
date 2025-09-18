"""Main Okta API client with authentication and error handling."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import httpx
from datetime import datetime, timedelta

from ..config import Settings
from ..exceptions import (
    AuthenticationError,
    OktaAPIError,
    RateLimitError,
    handle_okta_api_error,
)
from ..utils.logging import get_logger
from .users import UserManager
from .applications import ApplicationManager
from .logs import LogManager

logger = get_logger(__name__)


class OktaClient:
    """Main Okta API client with rate limiting and error handling."""

    def __init__(self, settings: Settings):
        """Initialize the Okta client.

        Args:
            settings: Application settings containing Okta configuration
        """
        self.settings = settings
        self._rate_limiter = RateLimiter(settings.okta_rate_limit)

        # Configure HTTP client
        self._client = httpx.AsyncClient(
            base_url=f"{settings.okta_org_url}/api/v1",
            timeout=settings.okta_timeout_seconds,
            headers=self._get_headers(),
        )

        # Initialize service managers
        self.users = UserManager(self)
        self.applications = ApplicationManager(self)
        self.logs = LogManager(self)

        logger.info(
            "Okta client initialized",
            org_url=settings.okta_org_url,
            auth_method="oauth" if settings.is_oauth_configured else "api_token",
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"mcp-okta-support/{self.settings.mcp_server_version}",
        }

        if self.settings.is_api_token_configured:
            headers["Authorization"] = f"SSWS {self.settings.okta_api_token}"
        elif self.settings.is_oauth_configured:
            # OAuth token will be handled separately
            pass

        return headers

    async def _get_oauth_token(self) -> str:
        """Get OAuth access token for API requests.

        Returns:
            Access token string
        """
        # This would implement OAuth client credentials flow
        # For now, returning a placeholder
        if not self.settings.is_oauth_configured:
            raise AuthenticationError("OAuth credentials not configured")

        # OAuth implementation would go here
        # This is a simplified placeholder
        return "oauth_token_placeholder"

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated API request with rate limiting.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: URL query parameters
            data: Request body data
            headers: Additional headers

        Returns:
            API response data

        Raises:
            OktaAPIError: For API errors
            RateLimitError: When rate limited
            AuthenticationError: For auth failures
        """
        await self._rate_limiter.acquire()

        # Update headers with OAuth token if configured
        request_headers = self._client.headers.copy()
        if headers:
            request_headers.update(headers)

        if self.settings.is_oauth_configured and "Authorization" not in request_headers:
            token = await self._get_oauth_token()
            request_headers["Authorization"] = f"Bearer {token}"

        try:
            logger.debug(
                "Making API request",
                method=method,
                endpoint=endpoint,
                has_params=bool(params),
                has_data=bool(data),
            )

            response = await self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=data,
                headers=request_headers,
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                self._rate_limiter.update_from_response(response.headers)
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=response.status_code,
                    retry_after=retry_after,
                )

            # Handle other error responses
            if not response.is_success:
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"errorSummary": response.text or "Unknown error"}

                raise handle_okta_api_error(response.status_code, error_data)

            # Update rate limiter with successful response
            self._rate_limiter.update_from_response(response.headers)

            # Return response data
            if response.content:
                return response.json()
            return {}

        except httpx.TimeoutException:
            raise OktaAPIError(
                f"Request timeout after {self.settings.okta_timeout_seconds} seconds",
                status_code=408,
            )
        except httpx.RequestError as e:
            raise OktaAPIError(f"Network error: {str(e)}")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, requests_per_minute: int = 100):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()

        # Track rate limit info from responses
        self.limit = requests_per_minute
        self.remaining = requests_per_minute
        self.reset_time = datetime.now() + timedelta(minutes=1)

    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        async with self.lock:
            now = datetime.now()

            # Remove old requests
            self.requests = [req_time for req_time in self.requests if now - req_time < timedelta(minutes=1)]

            # Check if we're at the limit
            if len(self.requests) >= self.requests_per_minute:
                sleep_time = 60 - (now - self.requests[0]).total_seconds()
                if sleep_time > 0:
                    logger.warning(
                        "Rate limit reached, sleeping",
                        sleep_seconds=sleep_time,
                        requests_count=len(self.requests),
                    )
                    await asyncio.sleep(sleep_time)

            # Check API-provided rate limit info
            if self.remaining <= 0 and now < self.reset_time:
                sleep_time = (self.reset_time - now).total_seconds()
                if sleep_time > 0:
                    logger.warning(
                        "API rate limit reached, sleeping",
                        sleep_seconds=sleep_time,
                        reset_time=self.reset_time.isoformat(),
                    )
                    await asyncio.sleep(sleep_time)

            # Record this request
            self.requests.append(now)

    def update_from_response(self, headers: Dict[str, str]) -> None:
        """Update rate limit info from API response headers.

        Args:
            headers: Response headers from Okta API
        """
        try:
            if "X-Rate-Limit-Limit" in headers:
                self.limit = int(headers["X-Rate-Limit-Limit"])
            if "X-Rate-Limit-Remaining" in headers:
                self.remaining = int(headers["X-Rate-Limit-Remaining"])
            if "X-Rate-Limit-Reset" in headers:
                reset_timestamp = int(headers["X-Rate-Limit-Reset"])
                self.reset_time = datetime.fromtimestamp(reset_timestamp)

            logger.debug(
                "Rate limit updated",
                limit=self.limit,
                remaining=self.remaining,
                reset_time=self.reset_time.isoformat(),
            )
        except (ValueError, KeyError) as e:
            logger.debug("Failed to parse rate limit headers", error=str(e))