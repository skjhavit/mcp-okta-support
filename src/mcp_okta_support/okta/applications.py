"""Application management operations for Okta API."""

from typing import Any, Dict, List, Optional
from urllib.parse import quote

from ..exceptions import ApplicationNotFoundError, ValidationError
from ..utils.logging import get_logger
from .models import OktaApplication, ApplicationConfig, OktaAPIResponse

logger = get_logger(__name__)


class ApplicationManager:
    """Manager for Okta application operations."""

    def __init__(self, client):
        """Initialize application manager.

        Args:
            client: OktaClient instance
        """
        self.client = client

    async def list_applications(
        self,
        limit: int = 20,
        filter_expr: Optional[str] = None,
        expand: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List applications in the organization.

        Args:
            limit: Maximum number of applications to return
            filter_expr: Optional filter expression
            expand: Optional expand parameter

        Returns:
            List of application data dictionaries
        """
        logger.info(
            "Listing applications",
            limit=limit,
            has_filter=bool(filter_expr),
            expand=expand,
        )

        params = {"limit": str(limit)}
        if filter_expr:
            params["filter"] = filter_expr
        if expand:
            params["expand"] = expand

        response_data = await self.client.request(
            "GET",
            "/apps",
            params=params,
        )

        applications = []
        for app_data in response_data:
            try:
                app = OktaApplication(**app_data)
                applications.append(app.dict())
            except Exception as e:
                logger.warning(
                    "Failed to parse application data",
                    app_id=app_data.get("id", "unknown"),
                    error=str(e),
                )
                # Include raw data if parsing fails
                applications.append(app_data)

        logger.info("Applications listed successfully", count=len(applications))
        return applications

    async def get_application(self, app_identifier: str) -> Dict[str, Any]:
        """Get application by ID or name.

        Args:
            app_identifier: Application ID or name

        Returns:
            Application data dictionary

        Raises:
            ApplicationNotFoundError: If application is not found
            ValidationError: If identifier is invalid
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        # URL encode the identifier to handle special characters
        encoded_identifier = quote(app_identifier.strip(), safe="")

        logger.info("Getting application", app_identifier=app_identifier)

        try:
            response_data = await self.client.request(
                "GET",
                f"/apps/{encoded_identifier}",
            )

            app = OktaApplication(**response_data)
            logger.info(
                "Application retrieved successfully",
                app_id=app.id,
                app_name=app.name,
                app_status=app.status,
            )

            return app.dict()

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ApplicationNotFoundError(app_identifier)
            raise

    async def update_application(
        self,
        app_identifier: str,
        config_updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update application configuration.

        Args:
            app_identifier: Application ID or name
            config_updates: Dictionary of configuration updates

        Returns:
            Updated application data dictionary

        Raises:
            ApplicationNotFoundError: If application is not found
            ValidationError: If updates are invalid
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        if not config_updates:
            raise ValidationError("config_updates", config_updates, "Cannot be empty")

        # Validate configuration updates
        try:
            config = ApplicationConfig(**config_updates)
            validated_updates = config.to_okta_format()
        except Exception as e:
            raise ValidationError("config_updates", config_updates, str(e))

        encoded_identifier = quote(app_identifier.strip(), safe="")

        logger.info(
            "Updating application configuration",
            app_identifier=app_identifier,
            update_fields=list(validated_updates.keys()),
        )

        try:
            response_data = await self.client.request(
                "PUT",
                f"/apps/{encoded_identifier}",
                data=validated_updates,
            )

            app = OktaApplication(**response_data)
            logger.info(
                "Application configuration updated successfully",
                app_id=app.id,
                updated_fields=list(validated_updates.keys()),
            )

            return app.dict()

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ApplicationNotFoundError(app_identifier)
            raise

    async def get_application_users(
        self,
        app_identifier: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get users assigned to an application.

        Args:
            app_identifier: Application ID or name
            limit: Maximum number of users to return

        Returns:
            List of user assignment data

        Raises:
            ApplicationNotFoundError: If application is not found
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        encoded_identifier = quote(app_identifier.strip(), safe="")

        logger.info(
            "Getting application users",
            app_identifier=app_identifier,
            limit=limit,
        )

        params = {"limit": str(limit)}

        try:
            response_data = await self.client.request(
                "GET",
                f"/apps/{encoded_identifier}/users",
                params=params,
            )

            logger.info(
                "Application users retrieved successfully",
                app_identifier=app_identifier,
                user_count=len(response_data),
            )

            return response_data

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ApplicationNotFoundError(app_identifier)
            raise

    async def get_application_groups(
        self,
        app_identifier: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get groups assigned to an application.

        Args:
            app_identifier: Application ID or name
            limit: Maximum number of groups to return

        Returns:
            List of group assignment data

        Raises:
            ApplicationNotFoundError: If application is not found
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        encoded_identifier = quote(app_identifier.strip(), safe="")

        logger.info(
            "Getting application groups",
            app_identifier=app_identifier,
            limit=limit,
        )

        params = {"limit": str(limit)}

        try:
            response_data = await self.client.request(
                "GET",
                f"/apps/{encoded_identifier}/groups",
                params=params,
            )

            logger.info(
                "Application groups retrieved successfully",
                app_identifier=app_identifier,
                group_count=len(response_data),
            )

            return response_data

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ApplicationNotFoundError(app_identifier)
            raise

    async def activate_application(self, app_identifier: str) -> Dict[str, Any]:
        """Activate an application.

        Args:
            app_identifier: Application ID or name

        Returns:
            Operation result

        Raises:
            ApplicationNotFoundError: If application is not found
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        encoded_identifier = quote(app_identifier.strip(), safe="")

        logger.info("Activating application", app_identifier=app_identifier)

        try:
            response_data = await self.client.request(
                "POST",
                f"/apps/{encoded_identifier}/lifecycle/activate",
            )

            logger.info(
                "Application activated successfully",
                app_identifier=app_identifier,
            )

            return {
                "success": True,
                "app_identifier": app_identifier,
                "action": "activate",
                "result": response_data,
            }

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ApplicationNotFoundError(app_identifier)
            raise

    async def deactivate_application(self, app_identifier: str) -> Dict[str, Any]:
        """Deactivate an application.

        Args:
            app_identifier: Application ID or name

        Returns:
            Operation result

        Raises:
            ApplicationNotFoundError: If application is not found
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        encoded_identifier = quote(app_identifier.strip(), safe="")

        logger.info("Deactivating application", app_identifier=app_identifier)

        try:
            response_data = await self.client.request(
                "POST",
                f"/apps/{encoded_identifier}/lifecycle/deactivate",
            )

            logger.info(
                "Application deactivated successfully",
                app_identifier=app_identifier,
            )

            return {
                "success": True,
                "app_identifier": app_identifier,
                "action": "deactivate",
                "result": response_data,
            }

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ApplicationNotFoundError(app_identifier)
            raise

    async def assign_user_to_application(
        self,
        app_identifier: str,
        user_id: str,
        app_user_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Assign a user to an application.

        Args:
            app_identifier: Application ID or name
            user_id: User ID to assign
            app_user_profile: Optional application-specific user profile

        Returns:
            Assignment result

        Raises:
            ApplicationNotFoundError: If application is not found
            ValidationError: If parameters are invalid
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        if not user_id or not user_id.strip():
            raise ValidationError("user_id", user_id, "Cannot be empty")

        encoded_identifier = quote(app_identifier.strip(), safe="")
        encoded_user_id = quote(user_id.strip(), safe="")

        logger.info(
            "Assigning user to application",
            app_identifier=app_identifier,
            user_id=user_id,
        )

        assignment_data = {
            "id": user_id,
            "scope": "USER",
        }

        if app_user_profile:
            assignment_data["profile"] = app_user_profile

        try:
            response_data = await self.client.request(
                "POST",
                f"/apps/{encoded_identifier}/users",
                data=assignment_data,
            )

            logger.info(
                "User assigned to application successfully",
                app_identifier=app_identifier,
                user_id=user_id,
            )

            return {
                "success": True,
                "app_identifier": app_identifier,
                "user_id": user_id,
                "action": "assign_user",
                "result": response_data,
            }

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ApplicationNotFoundError(app_identifier)
            raise

    async def unassign_user_from_application(
        self,
        app_identifier: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Unassign a user from an application.

        Args:
            app_identifier: Application ID or name
            user_id: User ID to unassign

        Returns:
            Operation result

        Raises:
            ApplicationNotFoundError: If application is not found
            ValidationError: If parameters are invalid
        """
        if not app_identifier or not app_identifier.strip():
            raise ValidationError("app_identifier", app_identifier, "Cannot be empty")

        if not user_id or not user_id.strip():
            raise ValidationError("user_id", user_id, "Cannot be empty")

        encoded_identifier = quote(app_identifier.strip(), safe="")
        encoded_user_id = quote(user_id.strip(), safe="")

        logger.info(
            "Unassigning user from application",
            app_identifier=app_identifier,
            user_id=user_id,
        )

        try:
            response_data = await self.client.request(
                "DELETE",
                f"/apps/{encoded_identifier}/users/{encoded_user_id}",
            )

            logger.info(
                "User unassigned from application successfully",
                app_identifier=app_identifier,
                user_id=user_id,
            )

            return {
                "success": True,
                "app_identifier": app_identifier,
                "user_id": user_id,
                "action": "unassign_user",
                "result": response_data,
            }

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ApplicationNotFoundError(app_identifier)
            raise