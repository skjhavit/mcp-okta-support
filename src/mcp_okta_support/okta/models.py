"""Pydantic models for Okta API responses and data structures."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class OktaUser(BaseModel):
    """Okta user model."""

    id: str
    status: str
    created: datetime
    activated: Optional[datetime] = None
    statusChanged: Optional[datetime] = None
    lastLogin: Optional[datetime] = None
    lastUpdated: datetime
    passwordChanged: Optional[datetime] = None
    type: Dict[str, str] = Field(default_factory=dict)
    profile: Dict[str, Any] = Field(default_factory=dict)
    credentials: Optional[Dict[str, Any]] = None
    _links: Optional[Dict[str, Any]] = Field(default=None, alias="_links")

    class Config:
        allow_population_by_field_name = True

    @property
    def login(self) -> Optional[str]:
        """Get user login from profile."""
        return self.profile.get("login")

    @property
    def email(self) -> Optional[str]:
        """Get user email from profile."""
        return self.profile.get("email")

    @property
    def first_name(self) -> Optional[str]:
        """Get user first name from profile."""
        return self.profile.get("firstName")

    @property
    def last_name(self) -> Optional[str]:
        """Get user last name from profile."""
        return self.profile.get("lastName")

    @property
    def display_name(self) -> str:
        """Get user display name."""
        first = self.first_name
        last = self.last_name
        if first and last:
            return f"{first} {last}"
        return self.login or self.email or self.id


class OktaApplication(BaseModel):
    """Okta application model."""

    id: str
    name: str
    label: str
    status: str
    lastUpdated: datetime
    created: datetime
    accessibility: Optional[Dict[str, Any]] = None
    visibility: Optional[Dict[str, Any]] = None
    features: List[str] = Field(default_factory=list)
    signOnMode: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    _links: Optional[Dict[str, Any]] = Field(default=None, alias="_links")

    class Config:
        allow_population_by_field_name = True

    @property
    def is_active(self) -> bool:
        """Check if application is active."""
        return self.status == "ACTIVE"


class OktaLogEvent(BaseModel):
    """Okta system log event model."""

    uuid: str
    published: datetime
    eventType: str
    version: str
    severity: str
    legacyEventType: Optional[str] = None
    displayMessage: Optional[str] = None
    actor: Optional[Dict[str, Any]] = None
    client: Optional[Dict[str, Any]] = None
    request: Optional[Dict[str, Any]] = None
    outcome: Optional[Dict[str, Any]] = None
    target: Optional[List[Dict[str, Any]]] = None
    transaction: Optional[Dict[str, Any]] = None
    debugContext: Optional[Dict[str, Any]] = None
    authenticationContext: Optional[Dict[str, Any]] = None
    securityContext: Optional[Dict[str, Any]] = None

    @property
    def is_success(self) -> bool:
        """Check if event outcome was successful."""
        if not self.outcome:
            return False
        return self.outcome.get("result") == "SUCCESS"

    @property
    def actor_name(self) -> Optional[str]:
        """Get actor display name."""
        if not self.actor:
            return None
        return self.actor.get("displayName") or self.actor.get("alternateId")

    @property
    def target_names(self) -> List[str]:
        """Get target display names."""
        if not self.target:
            return []
        names = []
        for target_item in self.target:
            name = target_item.get("displayName") or target_item.get("alternateId")
            if name:
                names.append(name)
        return names


class UserProfile(BaseModel):
    """User profile model for updates."""

    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    login: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    manager: Optional[str] = None
    mobilePhone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    countryCode: Optional[str] = None
    customAttributes: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def to_okta_format(self) -> Dict[str, Any]:
        """Convert to Okta API format."""
        profile_data = {}
        for field, value in self.dict(exclude_none=True).items():
            if field == "customAttributes":
                profile_data.update(value)
            else:
                profile_data[field] = value
        return profile_data


class ApplicationConfig(BaseModel):
    """Application configuration model for updates."""

    label: Optional[str] = None
    visibility: Optional[Dict[str, Any]] = None
    accessibility: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    features: Optional[List[str]] = None

    def to_okta_format(self) -> Dict[str, Any]:
        """Convert to Okta API format."""
        return self.dict(exclude_none=True)


class LogSearchParams(BaseModel):
    """Parameters for log search queries."""

    q: Optional[str] = None
    filter: Optional[str] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    sortOrder: str = Field(default="DESCENDING")
    limit: int = Field(default=100, ge=1, le=1000)
    after: Optional[str] = None

    @validator("sortOrder")
    def validate_sort_order(cls, v):
        """Validate sort order."""
        if v not in ["ASCENDING", "DESCENDING"]:
            raise ValueError("sortOrder must be ASCENDING or DESCENDING")
        return v

    def to_params(self) -> Dict[str, str]:
        """Convert to query parameters."""
        params = {}
        if self.q:
            params["q"] = self.q
        if self.filter:
            params["filter"] = self.filter
        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        params["sortOrder"] = self.sortOrder
        params["limit"] = str(self.limit)
        if self.after:
            params["after"] = self.after
        return params


class OktaAPIResponse(BaseModel):
    """Generic Okta API response wrapper."""

    data: Union[List[Any], Dict[str, Any], Any]
    links: Optional[Dict[str, str]] = None
    total_count: Optional[int] = None
    has_more: bool = False

    @classmethod
    def from_response(
        cls,
        data: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> "OktaAPIResponse":
        """Create response from API data and headers.

        Args:
            data: Response data
            headers: Response headers

        Returns:
            OktaAPIResponse instance
        """
        links = {}
        has_more = False

        if headers:
            # Parse Link header for pagination
            link_header = headers.get("Link", "")
            if link_header:
                for link in link_header.split(","):
                    parts = link.strip().split(";")
                    if len(parts) == 2:
                        url = parts[0].strip("<>")
                        rel = parts[1].strip().split("=")[1].strip('"')
                        links[rel] = url
                        if rel == "next":
                            has_more = True

        return cls(
            data=data,
            links=links,
            has_more=has_more,
        )


class PasswordResetRequest(BaseModel):
    """Password reset request model."""

    sendEmail: bool = Field(default=True)
    tempPassword: Optional[str] = None

    def to_okta_format(self) -> Dict[str, Any]:
        """Convert to Okta API format."""
        data = {"sendEmail": self.sendEmail}
        if self.tempPassword:
            data["tempPassword"] = self.tempPassword
        return data