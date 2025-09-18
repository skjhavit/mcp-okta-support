"""User management operations for Okta API."""

from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

from ..exceptions import UserNotFoundError, ValidationError
from ..utils.logging import get_logger
from .models import OktaUser, UserProfile, PasswordResetRequest, OktaAPIResponse

logger = get_logger(__name__)


class UserManager:
    """Manager for Okta user operations."""

    def __init__(self, client):
        """Initialize user manager.

        Args:
            client: OktaClient instance
        """
        self.client = client

    async def get_user(self, user_identifier: str) -> Dict[str, Any]:
        """Get user by ID, email, or login.

        Args:
            user_identifier: User ID, email, or login name

        Returns:
            User data dictionary

        Raises:
            UserNotFoundError: If user is not found
            ValidationError: If identifier is invalid
        """
        if not user_identifier or not user_identifier.strip():
            raise ValidationError("user_identifier", user_identifier, "Cannot be empty")

        # URL encode the identifier to handle special characters
        encoded_identifier = quote(user_identifier.strip(), safe="")

        logger.info("Getting user", user_identifier=user_identifier)

        try:
            response_data = await self.client.request(
                "GET",
                f"/users/{encoded_identifier}",
            )

            user = OktaUser(**response_data)
            logger.info(
                "User retrieved successfully",
                user_id=user.id,
                user_status=user.status,
                user_email=user.email,
            )

            return user.dict()

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise UserNotFoundError(user_identifier)
            raise

    async def list_users(
        self,
        limit: int = 200,
        filter_expr: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List users with optional filtering.

        Args:
            limit: Maximum number of users to return
            filter_expr: Okta filter expression
            search: Search query

        Returns:
            List of user data dictionaries
        """
        logger.info(
            "Listing users",
            limit=limit,
            has_filter=bool(filter_expr),
            has_search=bool(search),
        )

        params = {"limit": str(limit)}
        if filter_expr:
            params["filter"] = filter_expr
        if search:
            params["search"] = search

        response_data = await self.client.request(
            "GET",
            "/users",
            params=params,
        )

        users = [OktaUser(**user_data).dict() for user_data in response_data]
        logger.info("Users listed successfully", count=len(users))

        return users

    async def update_user_profile(
        self,
        user_identifier: str,
        profile_updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update user profile attributes.

        Args:
            user_identifier: User ID, email, or login name
            profile_updates: Dictionary of profile attributes to update

        Returns:
            Updated user data dictionary

        Raises:
            UserNotFoundError: If user is not found
            ValidationError: If updates are invalid
        """
        if not user_identifier or not user_identifier.strip():
            raise ValidationError("user_identifier", user_identifier, "Cannot be empty")

        if not profile_updates:
            raise ValidationError("profile_updates", profile_updates, "Cannot be empty")

        # Validate profile updates
        try:
            profile = UserProfile(**profile_updates)
            validated_updates = profile.to_okta_format()
        except Exception as e:
            raise ValidationError("profile_updates", profile_updates, str(e))

        encoded_identifier = quote(user_identifier.strip(), safe="")

        logger.info(
            "Updating user profile",
            user_identifier=user_identifier,
            update_fields=list(validated_updates.keys()),
        )

        try:
            response_data = await self.client.request(
                "POST",
                f"/users/{encoded_identifier}",
                data={"profile": validated_updates},
            )

            user = OktaUser(**response_data)
            logger.info(
                "User profile updated successfully",
                user_id=user.id,
                updated_fields=list(validated_updates.keys()),
            )

            return user.dict()

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise UserNotFoundError(user_identifier)
            raise

    async def reactivate_user(self, user_identifier: str) -> Dict[str, Any]:
        """Reactivate a user (re-invite).

        Args:
            user_identifier: User ID, email, or login name

        Returns:
            Operation result

        Raises:
            UserNotFoundError: If user is not found
        """
        if not user_identifier or not user_identifier.strip():
            raise ValidationError("user_identifier", user_identifier, "Cannot be empty")

        encoded_identifier = quote(user_identifier.strip(), safe="")

        logger.info("Reactivating user", user_identifier=user_identifier)

        try:
            response_data = await self.client.request(
                "POST",
                f"/users/{encoded_identifier}/lifecycle/reactivate",
                params={"sendEmail": "true"},
            )

            logger.info("User reactivated successfully", user_identifier=user_identifier)

            return {
                "success": True,
                "user_identifier": user_identifier,
                "action": "reactivate",
                "email_sent": True,
                "result": response_data,
            }

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise UserNotFoundError(user_identifier)
            raise

    async def unlock_user(self, user_identifier: str) -> Dict[str, Any]:
        """Unlock a locked user account.

        Args:
            user_identifier: User ID, email, or login name

        Returns:
            Operation result

        Raises:
            UserNotFoundError: If user is not found
        """
        if not user_identifier or not user_identifier.strip():
            raise ValidationError("user_identifier", user_identifier, "Cannot be empty")

        encoded_identifier = quote(user_identifier.strip(), safe="")

        logger.info("Unlocking user", user_identifier=user_identifier)

        try:
            response_data = await self.client.request(
                "POST",
                f"/users/{encoded_identifier}/lifecycle/unlock",
            )

            logger.info("User unlocked successfully", user_identifier=user_identifier)

            return {
                "success": True,
                "user_identifier": user_identifier,
                "action": "unlock",
                "result": response_data,
            }

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise UserNotFoundError(user_identifier)
            raise

    async def reset_password(
        self,
        user_identifier: str,
        send_email: bool = True,
    ) -> Dict[str, Any]:
        """Reset user password.

        Args:
            user_identifier: User ID, email, or login name
            send_email: Whether to send password reset email

        Returns:
            Operation result

        Raises:
            UserNotFoundError: If user is not found
        """
        if not user_identifier or not user_identifier.strip():
            raise ValidationError("user_identifier", user_identifier, "Cannot be empty")

        encoded_identifier = quote(user_identifier.strip(), safe="")

        logger.info(
            "Resetting user password",
            user_identifier=user_identifier,
            send_email=send_email,
        )

        # Prepare reset request
        reset_request = PasswordResetRequest(sendEmail=send_email)

        try:
            response_data = await self.client.request(
                "POST",
                f"/users/{encoded_identifier}/credentials/reset_password",
                data=reset_request.to_okta_format(),
            )

            logger.info(
                "User password reset successfully",
                user_identifier=user_identifier,
                email_sent=send_email,
            )

            return {
                "success": True,
                "user_identifier": user_identifier,
                "action": "reset_password",
                "email_sent": send_email,
                "result": response_data,
            }

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise UserNotFoundError(user_identifier)
            raise

    async def get_user_groups(self, user_identifier: str) -> List[Dict[str, Any]]:
        """Get groups that a user belongs to.

        Args:
            user_identifier: User ID, email, or login name

        Returns:
            List of group data dictionaries

        Raises:
            UserNotFoundError: If user is not found
        """
        if not user_identifier or not user_identifier.strip():
            raise ValidationError("user_identifier", user_identifier, "Cannot be empty")

        encoded_identifier = quote(user_identifier.strip(), safe="")

        logger.info("Getting user groups", user_identifier=user_identifier)

        try:
            response_data = await self.client.request(
                "GET",
                f"/users/{encoded_identifier}/groups",
            )

            logger.info(
                "User groups retrieved successfully",
                user_identifier=user_identifier,
                group_count=len(response_data),
            )

            return response_data

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise UserNotFoundError(user_identifier)
            raise

    async def get_user_applications(self, user_identifier: str) -> List[Dict[str, Any]]:
        """Get applications assigned to a user.

        Args:
            user_identifier: User ID, email, or login name

        Returns:
            List of application assignment data

        Raises:
            UserNotFoundError: If user is not found
        """
        if not user_identifier or not user_identifier.strip():
            raise ValidationError("user_identifier", user_identifier, "Cannot be empty")

        encoded_identifier = quote(user_identifier.strip(), safe="")

        logger.info("Getting user applications", user_identifier=user_identifier)

        try:
            response_data = await self.client.request(
                "GET",
                f"/users/{encoded_identifier}/appLinks",
            )

            logger.info(
                "User applications retrieved successfully",
                user_identifier=user_identifier,
                app_count=len(response_data),
            )

            return response_data

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise UserNotFoundError(user_identifier)
            raise