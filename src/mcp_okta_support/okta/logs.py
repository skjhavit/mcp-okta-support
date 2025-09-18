"""System log operations for Okta API."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from ..exceptions import ValidationError
from ..utils.logging import get_logger
from .models import OktaLogEvent, LogSearchParams, OktaAPIResponse

logger = get_logger(__name__)


class LogManager:
    """Manager for Okta system log operations."""

    def __init__(self, client):
        """Initialize log manager.

        Args:
            client: OktaClient instance
        """
        self.client = client

    async def get_logs(
        self,
        since: Optional[str] = None,
        until: Optional[str] = None,
        filter_expr: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 100,
        sort_order: str = "DESCENDING",
    ) -> List[Dict[str, Any]]:
        """Get system logs with optional filtering.

        Args:
            since: ISO timestamp to filter logs since this time
            until: ISO timestamp to filter logs until this time
            filter_expr: Okta filter expression
            query: Search query
            limit: Maximum number of log entries to return
            sort_order: Sort order (ASCENDING or DESCENDING)

        Returns:
            List of log entry dictionaries
        """
        logger.info(
            "Getting system logs",
            since=since,
            until=until,
            has_filter=bool(filter_expr),
            has_query=bool(query),
            limit=limit,
            sort_order=sort_order,
        )

        # Build search parameters
        search_params = LogSearchParams(
            filter=filter_expr,
            q=query,
            since=datetime.fromisoformat(since.replace("Z", "+00:00")) if since else None,
            until=datetime.fromisoformat(until.replace("Z", "+00:00")) if until else None,
            limit=limit,
            sortOrder=sort_order,
        )

        params = search_params.to_params()

        response_data = await self.client.request(
            "GET",
            "/logs",
            params=params,
        )

        logs = []
        for log_data in response_data:
            try:
                log_event = OktaLogEvent(**log_data)
                logs.append(log_event.dict())
            except Exception as e:
                logger.warning(
                    "Failed to parse log event",
                    event_id=log_data.get("uuid", "unknown"),
                    error=str(e),
                )
                # Include raw data if parsing fails
                logs.append(log_data)

        logger.info("System logs retrieved successfully", count=len(logs))
        return logs

    async def get_user_logs(
        self,
        user_identifier: str,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get system logs for a specific user.

        Args:
            user_identifier: User ID, email, or login name
            since: ISO timestamp to filter logs since this time
            limit: Maximum number of log entries to return

        Returns:
            List of user-related log entries

        Raises:
            ValidationError: If user_identifier is invalid
        """
        if not user_identifier or not user_identifier.strip():
            raise ValidationError("user_identifier", user_identifier, "Cannot be empty")

        logger.info(
            "Getting user logs",
            user_identifier=user_identifier,
            since=since,
            limit=limit,
        )

        # Build filter for user-related events
        # Include both actor and target references to the user
        user_filter_parts = []

        # Check if it looks like an email
        if "@" in user_identifier:
            user_filter_parts.extend([
                f'actor.alternateId eq "{user_identifier}"',
                f'target.alternateId eq "{user_identifier}"',
            ])
        else:
            # Assume it's a user ID or login
            user_filter_parts.extend([
                f'actor.id eq "{user_identifier}"',
                f'target.id eq "{user_identifier}"',
                f'actor.alternateId eq "{user_identifier}"',
                f'target.alternateId eq "{user_identifier}"',
            ])

        # Combine filters with OR
        user_filter = " or ".join(user_filter_parts)

        return await self.get_logs(
            since=since,
            filter_expr=user_filter,
            limit=limit,
        )

    async def get_application_logs(
        self,
        app_identifier: str,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get system logs for a specific application.

        Args:
            app_identifier: Application ID or name
            since: ISO timestamp to filter logs since this time
            limit: Maximum number of log entries to return

        Returns:
            List of application-related log entries

        Raises:
            ValidationError: If app_identifier is invalid
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        logger.info(
            "Getting application logs",
            app_identifier=app_identifier,
            since=since,
            limit=limit,
        )

        # Build filter for application-related events
        app_filter_parts = [
            f'target.id eq "{app_identifier}"',
            f'target.alternateId eq "{app_identifier}"',
            f'target.displayName eq "{app_identifier}"',
        ]

        # Combine filters with OR
        app_filter = " or ".join(app_filter_parts)

        return await self.get_logs(
            since=since,
            filter_expr=app_filter,
            limit=limit,
        )

    async def search_logs(
        self,
        query: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search system logs with a query expression.

        Args:
            query: Search query or filter expression
            since: ISO timestamp to filter logs since this time
            until: ISO timestamp to filter logs until this time
            limit: Maximum number of log entries to return

        Returns:
            List of matching log entries

        Raises:
            ValidationError: If query is invalid
        """
        if not query or not query.strip():
            raise ValidationError("query", query, "Cannot be empty")

        logger.info(
            "Searching system logs",
            query=query,
            since=since,
            until=until,
            limit=limit,
        )

        # Determine if query is a filter expression or search query
        # Filter expressions typically contain operators like 'eq', 'sw', etc.
        is_filter_expr = any(
            op in query.lower()
            for op in ["eq ", "ne ", "sw ", "ew ", "co ", "gt ", "ge ", "lt ", "le "]
        )

        if is_filter_expr:
            return await self.get_logs(
                since=since,
                until=until,
                filter_expr=query,
                limit=limit,
            )
        else:
            return await self.get_logs(
                since=since,
                until=until,
                query=query,
                limit=limit,
            )

    async def get_failed_login_attempts(
        self,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get failed login attempts.

        Args:
            since: ISO timestamp to filter logs since this time
            limit: Maximum number of log entries to return

        Returns:
            List of failed login log entries
        """
        logger.info(
            "Getting failed login attempts",
            since=since,
            limit=limit,
        )

        filter_expr = 'eventType eq "user.session.start" and outcome.result eq "FAILURE"'

        return await self.get_logs(
            since=since,
            filter_expr=filter_expr,
            limit=limit,
        )

    async def get_password_reset_events(
        self,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get password reset events.

        Args:
            since: ISO timestamp to filter logs since this time
            limit: Maximum number of log entries to return

        Returns:
            List of password reset log entries
        """
        logger.info(
            "Getting password reset events",
            since=since,
            limit=limit,
        )

        filter_expr = 'eventType eq "user.account.reset_password"'

        return await self.get_logs(
            since=since,
            filter_expr=filter_expr,
            limit=limit,
        )

    async def get_admin_actions(
        self,
        admin_identifier: str,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get actions performed by a specific admin user.

        Args:
            admin_identifier: Admin user ID, email, or login
            since: ISO timestamp to filter logs since this time
            limit: Maximum number of log entries to return

        Returns:
            List of admin action log entries

        Raises:
            ValidationError: If admin_identifier is invalid
        """
        if not admin_identifier or not admin_identifier.strip():
            raise ValidationError("admin_identifier", admin_identifier, "Cannot be empty")

        logger.info(
            "Getting admin actions",
            admin_identifier=admin_identifier,
            since=since,
            limit=limit,
        )

        # Build filter for admin actions
        if "@" in admin_identifier:
            filter_expr = f'actor.alternateId eq "{admin_identifier}"'
        else:
            filter_expr = f'actor.id eq "{admin_identifier}" or actor.alternateId eq "{admin_identifier}"'

        return await self.get_logs(
            since=since,
            filter_expr=filter_expr,
            limit=limit,
        )

    async def get_suspicious_activity(
        self,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get potentially suspicious activity (warnings and errors).

        Args:
            since: ISO timestamp to filter logs since this time
            limit: Maximum number of log entries to return

        Returns:
            List of suspicious activity log entries
        """
        logger.info(
            "Getting suspicious activity",
            since=since,
            limit=limit,
        )

        filter_expr = 'severity eq "WARN" or severity eq "ERROR"'

        return await self.get_logs(
            since=since,
            filter_expr=filter_expr,
            limit=limit,
        )

    async def get_recent_activity_summary(
        self,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """Get a summary of recent activity.

        Args:
            hours: Number of hours to look back

        Returns:
            Activity summary dictionary
        """
        logger.info("Getting recent activity summary", hours=hours)

        # Calculate since timestamp
        since_time = datetime.now() - timedelta(hours=hours)
        since_str = since_time.isoformat() + "Z"

        # Get various types of events
        all_logs = await self.get_logs(since=since_str, limit=1000)
        failed_logins = await self.get_failed_login_attempts(since=since_str, limit=100)
        password_resets = await self.get_password_reset_events(since=since_str, limit=100)
        suspicious = await self.get_suspicious_activity(since=since_str, limit=100)

        # Count event types
        event_type_counts = {}
        for log in all_logs:
            event_type = log.get("eventType", "unknown")
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        summary = {
            "timeframe": f"Last {hours} hours",
            "since": since_str,
            "total_events": len(all_logs),
            "failed_logins": len(failed_logins),
            "password_resets": len(password_resets),
            "suspicious_events": len(suspicious),
            "event_type_breakdown": event_type_counts,
            "top_event_types": sorted(
                event_type_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10],
        }

        logger.info(
            "Activity summary generated",
            total_events=summary["total_events"],
            failed_logins=summary["failed_logins"],
            suspicious_events=summary["suspicious_events"],
        )

        return summary