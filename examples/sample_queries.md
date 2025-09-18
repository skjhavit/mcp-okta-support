# Sample Queries for MCP Okta Support

This file contains example natural language queries you can use with your local LLM once MCP Okta Support is connected.

## User Management Queries

### Getting User Information
```
"Get details for user john.doe@company.com"
"Show me information about user ID 00u1a2b3c4d5e6f7g8h9"
"What are the details for user johndoe?"
"Tell me about the user with email jane.smith@company.com"
"Look up user information for the person with login j.doe"
"Show me my own user details"
```

### Updating User Profiles
```
"Update user john.doe@company.com's title to 'Senior Engineer'"
"Change the department for user ID 00u1a2b3c4d5e6f7 to 'Marketing'"
"Update user johndoe's manager to jane.smith@company.com"
"Set the phone number for jane.smith@company.com to +1-555-0123"
"Change John Doe's first name to 'Jonathan'"
"Update multiple fields for user alice@company.com: title to 'Team Lead' and department to 'Product'"
```

### Account Management
```
"Unlock account for user john.doe@company.com"
"Reset password for user jane.smith@company.com"
"Re-invite user bob.wilson@company.com"
"Send password reset email to user alice@company.com"
"Unlock the locked user account for david@company.com"
"Reactivate user sarah.jones@company.com"
```

### User Searches and Lists
```
"List all users in the Engineering department"
"Find users with title containing 'Manager'"
"Show me users created in the last week"
"Get all inactive users"
"Find users with no manager assigned"
"List users who haven't logged in for 30 days"
```

## Application Management Queries

### Application Information
```
"Show me all applications"
"List the first 10 applications"
"Get details for application 'Slack'"
"Show me information about app ID 0oa1b2c3d4e5f6g7"
"What applications are available in our organization?"
"Find applications with 'SAML' in the configuration"
```

### Application Configuration
```
"Update application 'Slack' label to 'Company Slack'"
"Change the visibility settings for app 'My Custom App'"
"Update the base URL for 'Jira' to https://newjira.company.com"
"Show me the configuration for the 'Office 365' application"
"List applications that are currently inactive"
"Get all SAML applications"
```

### Application Assignments
```
"Show users assigned to application 'Slack'"
"Get groups assigned to the 'Jira' application"
"List all applications assigned to user john.doe@company.com"
"Show me which users have access to 'Office 365'"
"Find applications with no user assignments"
"Get assignment details for app 'Salesforce'"
```

## System Logs and Monitoring Queries

### Login and Authentication
```
"Show me recent login failures"
"Find failed login attempts in the last 24 hours"
"Get successful logins for user john.doe@company.com"
"Show me all authentication events from yesterday"
"Find suspicious login activities"
"Get login attempts from unusual locations"
```

### Password and Security Events
```
"Show password reset events from last week"
"Find password change activities"
"Get account lockout events"
"Show me security-related warnings"
"Find suspicious user activities"
"Get multi-factor authentication events"
```

### User Activity Tracking
```
"Show logs for user john.doe@company.com from the last 24 hours"
"Get recent activity for user ID 00u1a2b3c4d5e6f7"
"What has alice@company.com been doing this week?"
"Show me user creation events from yesterday"
"Find user deactivation activities"
"Get profile change events for the last month"
```

### Application Activity
```
"Show app assignment events for 'Slack'"
"Get application access logs for 'Jira'"
"Find SSO events for the last week"
"Show me app configuration changes"
"Get application creation events"
"Find app deactivation activities"
```

### Administrative Activities
```
"Show admin actions by jane.admin@company.com"
"Find all administrative changes made today"
"Get user modification events by admins"
"Show me admin login activities"
"Find policy changes made by administrators"
"Get all admin actions in the last week"
```

### System Health and Monitoring
```
"Show me system errors from the last hour"
"Find API rate limit events"
"Get system warning messages"
"Show me recent system configuration changes"
"Find integration errors with external systems"
"Get performance-related events"
```

## Advanced and Complex Queries

### Bulk Operations
```
"For all users in the Engineering department, check their last login date"
"Update all users with title 'Intern' to have department 'Learning'"
"Find all users without manager assignments and list them"
"Get application assignments for all users created this month"
"Check which applications have been accessed in the last week"
```

### Conditional Logic
```
"If user john.doe@company.com is locked, unlock the account"
"For users inactive for 30+ days, show their profile details"
"If application 'Old System' exists, show its current status"
"For users without MFA, check their recent login patterns"
"If there are failed logins today, show the details"
```

### Analytics and Reporting
```
"Generate a summary of user activities for the last week"
"Show me the most accessed applications this month"
"Create a report of password reset activities"
"Analyze login patterns for security anomalies"
"Generate user onboarding statistics for Q1"
"Show application usage trends"
```

### Troubleshooting Scenarios
```
"Help me troubleshoot why user alice@company.com can't access Slack"
"Find out why bob@company.com's account is locked"
"Investigate failed login attempts for user charlie@company.com"
"Check if there are any issues with the 'Jira' application"
"Diagnose authentication problems for user diana@company.com"
"Investigate suspicious activities for user eve@company.com"
```

## Workflow Examples

### New User Onboarding
```
1. "Create user profile for new employee john.smith@company.com"
2. "Set john.smith@company.com's department to 'Engineering' and title to 'Software Engineer'"
3. "Assign applications 'Slack', 'Jira', and 'Office 365' to john.smith@company.com"
4. "Send welcome email to john.smith@company.com"
```

### User Offboarding
```
1. "Deactivate user leaving.employee@company.com"
2. "Remove all application assignments for leaving.employee@company.com"
3. "Generate a report of all activities by leaving.employee@company.com"
4. "Transfer manager assignments from leaving.employee@company.com to new.manager@company.com"
```

### Security Investigation
```
1. "Find all failed login attempts in the last 24 hours"
2. "For each failed login, check if the account was subsequently locked"
3. "Identify users with multiple failed logins from different locations"
4. "Generate a security incident report for suspicious activities"
```

### Application Audit
```
1. "List all applications and their current status"
2. "For each application, show the number of assigned users"
3. "Identify applications with no recent usage"
4. "Generate an application compliance report"
```

## Tips for Better Results

### Be Specific
- Use exact email addresses or user IDs when possible
- Specify time ranges for log searches
- Include specific application names

### Use Natural Language
- Ask questions as you would to a human administrator
- Use complete sentences for complex operations
- Combine multiple related requests

### Error Handling
- If a query fails, try rephrasing it
- Check user permissions if operations are denied
- Use more specific identifiers if searches return too many results

### Performance Optimization
- Limit large searches with time ranges
- Use filters to narrow down results
- Break complex operations into smaller steps