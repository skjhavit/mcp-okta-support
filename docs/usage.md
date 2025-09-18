# Usage Guide

This guide provides comprehensive examples of how to use MCP Okta Support with natural language commands through your local LLM.

## Quick Reference

### User Management
- [Get User Details](#get-user-details)
- [Update User Profile](#update-user-profile)
- [Unlock User Account](#unlock-user-account)
- [Reset User Password](#reset-user-password)
- [Re-invite User](#re-invite-user)

### Application Management
- [List Applications](#list-applications)
- [Get Application Details](#get-application-details)
- [Update Application Configuration](#update-application-configuration)

### System Logs
- [Get User Activity Logs](#get-user-activity-logs)
- [Search System Logs](#search-system-logs)
- [Find Specific Events](#find-specific-events)

## User Management

### Get User Details

**Description**: Retrieve comprehensive information about a user.

**Natural Language Examples**:
```
"Get details for user john.doe@company.com"
"Show me information about user ID 00u1a2b3c4d5e6f7g8h9"
"What are the details for user johndoe?"
"Tell me about the user with email jane.smith@company.com"
"Look up user information for j.doe"
```

**Response Example**:
```json
{
  "success": true,
  "user": {
    "id": "00u1a2b3c4d5e6f7g8h9",
    "status": "ACTIVE",
    "created": "2024-01-15T10:30:00.000Z",
    "lastLogin": "2024-01-20T14:22:00.000Z",
    "profile": {
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@company.com",
      "login": "john.doe@company.com",
      "title": "Software Engineer",
      "department": "Engineering"
    }
  },
  "message": "Successfully retrieved user details for john.doe@company.com"
}
```

### Update User Profile

**Description**: Modify user profile attributes.

**Natural Language Examples**:
```
"Update user john.doe@company.com's title to 'Senior Engineer'"
"Change the department for user ID 00u1a2b3c4d5e6f7 to 'Marketing'"
"Update user johndoe's manager to jane.smith@company.com"
"Set the phone number for jane.smith@company.com to +1-555-0123"
"Change John Doe's first name to 'Jonathan'"
```

**Supported Attributes**:
- `firstName`, `lastName`
- `email`, `title`, `department`
- `manager`, `mobilePhone`
- `city`, `state`, `zipCode`, `countryCode`
- Custom attributes via `customAttributes`

**Example Update**:
```
User: "Update user john.doe@company.com to have title 'Senior Engineer' and department 'R&D'"

Response: Successfully updated profile for john.doe@company.com with new title and department.
```

### Unlock User Account

**Description**: Unlock a locked user account (typically locked due to failed login attempts).

**Natural Language Examples**:
```
"Unlock account for user john.doe@company.com"
"Unlock user ID 00u1a2b3c4d5e6f7g8h9"
"Please unlock the account for johndoe"
"Remove the lock from jane.smith@company.com's account"
"Unlock the locked user account for j.doe"
```

**Use Cases**:
- User exceeded failed login attempts
- Account was manually locked
- Security policy triggered account lock

### Reset User Password

**Description**: Initiate password reset process for a user.

**Natural Language Examples**:
```
"Reset password for user john.doe@company.com"
"Send password reset email to user ID 00u1a2b3c4d5e6f7"
"Initiate password reset for johndoe"
"Reset the password for jane.smith@company.com and send email"
"Force password reset for user j.doe without sending email"
```

**Options**:
- **With email** (default): User receives reset instructions
- **Without email**: Admin manages the reset process

### Re-invite User

**Description**: Re-send invitation email to a user (typically for users in STAGED status).

**Natural Language Examples**:
```
"Re-invite user john.doe@company.com"
"Send invitation again to user ID 00u1a2b3c4d5e6f7"
"Resend the invitation email for johndoe"
"Re-invite the user jane.smith@company.com"
"Send another invitation to j.doe"
```

**Use Cases**:
- User never received original invitation
- Invitation email was lost or expired
- User needs to reactivate their account

## Application Management

### List Applications

**Description**: Retrieve a list of applications in your Okta organization.

**Natural Language Examples**:
```
"Show me all applications"
"List the first 10 applications"
"Get all apps in our organization"
"Show applications with 'SAML' in the name"
"List active applications only"
```

**Advanced Filtering**:
```
"Show me applications where status equals ACTIVE"
"List applications created after January 1, 2024"
"Find applications with 'Slack' in the label"
```

**Response Example**:
```json
{
  "success": true,
  "applications": [
    {
      "id": "0oa1b2c3d4e5f6g7h8i9",
      "name": "slack",
      "label": "Slack",
      "status": "ACTIVE",
      "signOnMode": "SAML_2_0"
    }
  ],
  "count": 15,
  "message": "Successfully retrieved 15 applications"
}
```

### Get Application Details

**Description**: Retrieve detailed information about a specific application.

**Natural Language Examples**:
```
"Get details for application 'Slack'"
"Show me information about app ID 0oa1b2c3d4e5f6g7"
"What are the details for the Slack application?"
"Tell me about the app named 'My Custom App'"
"Look up application configuration for Jira"
```

**Response Includes**:
- Basic application information
- Configuration settings
- Sign-on mode and URLs
- User/group assignments summary

### Update Application Configuration

**Description**: Modify application settings and configuration.

**Natural Language Examples**:
```
"Update application 'Slack' label to 'Company Slack'"
"Change the visibility settings for app ID 0oa1b2c3d4e5f6g7"
"Update the base URL for 'My App' to https://newurl.company.com"
"Modify the SAML settings for the Jira application"
"Hide the app 'Old System' from users"
```

**Configurable Settings**:
- `label`: Display name
- `visibility`: Who can see the app
- `settings.app`: Application-specific settings
- `settings.signOn`: Authentication settings
- `features`: Enabled features

## System Logs

### Get User Activity Logs

**Description**: Retrieve activity logs for a specific user.

**Natural Language Examples**:
```
"Show logs for user john.doe@company.com from the last 24 hours"
"Get recent activity for user ID 00u1a2b3c4d5e6f7"
"What has johndoe been doing in the last week?"
"Show me login attempts for jane.smith@company.com"
"Get all events for user j.doe since yesterday"
```

**Time Ranges**:
- "last hour", "last 24 hours", "last week"
- Specific dates: "since January 1, 2024"
- Custom ISO timestamps

### Search System Logs

**Description**: Search logs using queries and filters.

**Natural Language Examples**:
```
"Find all failed login attempts"
"Show password reset events from last week"
"Search for admin actions by jane.admin@company.com"
"Find all events with severity ERROR"
"Show me user creation events from yesterday"
```

**Common Search Patterns**:

#### Failed Login Attempts
```
"Find failed logins in the last 24 hours"
"Show me unsuccessful authentication attempts"
"Get all login failures for user john.doe@company.com"
```

#### Password Events
```
"Find password reset events"
"Show password change activities"
"Get password-related events for the last week"
```

#### Admin Activities
```
"Show admin actions by jane.admin@company.com"
"Find all administrative changes made today"
"Get user modification events by admins"
```

#### Application Events
```
"Show app assignment events"
"Find application creation activities"
"Get SSO events for Slack app"
```

### Find Specific Events

**Description**: Search for specific types of system events.

**Event Type Examples**:

#### User Lifecycle Events
```
"Show user creation events"
"Find user deactivation activities"
"Get user reactivation events"
```

#### Application Events
```
"Show application assignment events"
"Find app configuration changes"
"Get application access events"
```

#### Security Events
```
"Find suspicious activities"
"Show security warning events"
"Get authentication failures"
```

#### System Events
```
"Show API access events"
"Find rate limit exceeded events"
"Get system error events"
```

## Advanced Usage

### Combining Operations

**Example Workflow**:
```
1. "Find users created in the last week"
2. "For each new user, check their application assignments"
3. "Send welcome email to users without app assignments"
```

### Bulk Operations

**Pattern**:
```
"Get all users in the Engineering department"
"For each user, check their last login date"
"Send re-activation email to users inactive for 30+ days"
```

### Conditional Logic

**Examples**:
```
"If user john.doe@company.com is locked, unlock the account"
"For users with title 'Intern', update department to 'Learning'"
"If application 'Old System' exists, deactivate it"
```

## Response Handling

### Success Responses

All successful operations return:
```json
{
  "success": true,
  "data": { /* operation-specific data */ },
  "message": "Descriptive success message"
}
```

### Error Responses

Failed operations return:
```json
{
  "success": false,
  "error": "Error description",
  "error_type": "SpecificErrorType",
  "details": { /* additional error context */ }
}
```

### Common Error Types

- **UserNotFoundError**: User doesn't exist
- **ApplicationNotFoundError**: Application doesn't exist
- **AuthenticationError**: Invalid credentials
- **AuthorizationError**: Insufficient permissions
- **RateLimitError**: Too many requests
- **ValidationError**: Invalid input parameters

## Best Practices

### User Identification

**Preferred Formats**:
- Email address: `john.doe@company.com`
- User ID: `00u1a2b3c4d5e6f7g8h9`
- Login name: `johndoe`

### Application Identification

**Preferred Formats**:
- Application label: `Slack`
- Application ID: `0oa1b2c3d4e5f6g7h8i9`
- Application name: `slack`

### Time Specifications

**Supported Formats**:
- Relative: "last hour", "yesterday", "last week"
- Absolute: "January 1, 2024", "2024-01-01"
- ISO timestamps: "2024-01-01T00:00:00Z"

### Query Optimization

**Tips for Better Performance**:
- Use specific time ranges for log searches
- Limit result counts when exploring
- Use filters instead of broad searches
- Combine related operations in single requests

## Troubleshooting Commands

### Connectivity Tests
```
"Test connection to Okta"
"Check server health"
"Verify my authentication"
```

### Diagnostic Information
```
"Show my current rate limit status"
"Get server configuration info"
"Display available tools and resources"
```

### Error Recovery
```
"Retry the last failed operation"
"Clear any cached authentication tokens"
"Reset connection to Okta API"
```