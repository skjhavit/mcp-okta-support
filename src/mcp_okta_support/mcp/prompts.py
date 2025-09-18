"""MCP prompt definitions for the Okta Support Agent."""

from typing import Dict, Any
from pathlib import Path


def get_system_prompt() -> str:
    """Get the comprehensive system prompt for the Okta Support Agent.

    Returns:
        The complete system prompt as a string
    """
    # Try enhanced prompt first, fallback to original
    enhanced_prompt_file = Path(__file__).parent.parent / "prompts" / "enhanced_system_prompt.md"
    original_prompt_file = Path(__file__).parent.parent / "prompts" / "system_prompt.md"

    try:
        with open(enhanced_prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        try:
            with open(original_prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback inline prompt if neither file found
            return get_fallback_system_prompt()


def get_fallback_system_prompt() -> str:
    """Fallback system prompt if the markdown file is not available."""
    return """
# Okta Support Agent

You are an expert Okta Support Agent with comprehensive access to Okta management tools. Your role is to help users troubleshoot and resolve Okta-related issues through intelligent investigation and problem-solving.

## Your Purpose
- Systematically investigate user issues using available MCP tools
- Diagnose root causes through evidence-based analysis
- Resolve issues when possible or provide clear guidance
- Always ask for user confirmation before making changes

## Investigation Methodology
1. **UNDERSTAND** - Clarify the specific issue and gather details
2. **INVESTIGATE** - Use tools to check user status, logs, and related data
3. **DIAGNOSE** - Identify the root cause based on evidence
4. **RESOLVE** - Propose and execute solutions with user consent
5. **VERIFY** - Confirm resolution and provide next steps

## Available Tools
- User management: get details, unlock accounts, reset passwords
- Application management: check app status and assignments
- System logs: search for events, failed logins, security issues

## Key Principles
- Always investigate before concluding
- Get user consent before making changes
- Explain findings clearly in non-technical terms
- Be proactive in identifying related issues
- Follow security best practices

For login issues: Check user status → Review recent activity → Look for failed attempts → Identify cause → Propose solution

For app access issues: Verify user status → Check app assignments → Review SSO logs → Diagnose configuration → Resolve access

Always be helpful, thorough, and security-conscious in your assistance.
"""


def get_conversation_starters() -> Dict[str, str]:
    """Get example conversation starters for different issue types.

    Returns:
        Dictionary of issue types and example user queries
    """
    return {
        "login_issues": [
            "I can't login to Okta",
            "My account seems to be locked",
            "I'm getting an error when trying to sign in",
            "Login page won't accept my password"
        ],
        "app_access_issues": [
            "I can't access Salesforce",
            "Slack app is not showing up in my dashboard",
            "Getting SSO error when trying to access Jira",
            "Application won't load after clicking from Okta"
        ],
        "account_issues": [
            "My account was disabled",
            "I need to reset my password",
            "Haven't received the invitation email",
            "Profile information needs to be updated"
        ],
        "general_support": [
            "How do I add MFA to my account?",
            "What applications do I have access to?",
            "Why did I get a security alert email?",
            "Can you check my recent activity?"
        ]
    }


def get_diagnostic_prompts() -> Dict[str, str]:
    """Get diagnostic prompt templates for different investigation phases.

    Returns:
        Dictionary of diagnostic prompt templates
    """
    return {
        "initial_investigation": "Let me investigate this issue for you. First, I'll check your account status and recent activity...",

        "user_status_check": "I'm checking your user account details including status, last login, and profile information...",

        "log_analysis": "Now let me examine the system logs to understand what happened around the time you experienced this issue...",

        "root_cause_found": "I've identified the issue: {root_cause}. Here's what happened: {explanation}",

        "solution_proposal": "I can resolve this by {proposed_action}. This will {expected_outcome}. Would you like me to proceed?",

        "resolution_confirmation": "✅ Done! {action_taken}. {verification_steps}",

        "follow_up": "To prevent this in the future: {prevention_tips}. Is there anything else I can help you with?"
    }


def get_troubleshooting_workflows() -> Dict[str, Dict[str, Any]]:
    """Get structured troubleshooting workflows for common issues.

    Returns:
        Dictionary of issue types with their investigation steps
    """
    return {
        "login_failure": {
            "description": "User cannot login to Okta",
            "investigation_steps": [
                {
                    "step": "check_user_status",
                    "tool": "get_user_details",
                    "purpose": "Verify account status and basic information",
                    "success_criteria": "User status is ACTIVE",
                    "failure_actions": ["unlock_account", "reactivate_user"]
                },
                {
                    "step": "check_recent_attempts",
                    "tool": "get_user_logs",
                    "purpose": "Look for recent login attempts and patterns",
                    "timeframe": "24 hours",
                    "focus": ["authentication events", "failed attempts"]
                },
                {
                    "step": "check_failed_logins",
                    "tool": "get_failed_login_attempts",
                    "purpose": "Identify specific failure reasons",
                    "analysis": ["attempt count", "failure reasons", "source IPs"]
                },
                {
                    "step": "check_lockout_events",
                    "tool": "search_logs",
                    "query": "eventType eq \"user.account.lock\"",
                    "purpose": "Determine if account was locked and why"
                }
            ],
            "common_solutions": [
                {"issue": "LOCKED_OUT", "action": "unlock_user_account"},
                {"issue": "DEPROVISIONED", "action": "contact_admin"},
                {"issue": "PASSWORD_EXPIRED", "action": "reset_user_password"},
                {"issue": "MFA_REQUIRED", "action": "guide_mfa_setup"}
            ]
        },

        "app_access_failure": {
            "description": "User cannot access a specific application",
            "investigation_steps": [
                {
                    "step": "verify_user_status",
                    "tool": "get_user_details",
                    "purpose": "Ensure user account is active"
                },
                {
                    "step": "check_app_status",
                    "tool": "get_application_details",
                    "purpose": "Verify application is active and properly configured"
                },
                {
                    "step": "check_user_assignments",
                    "tool": "get_user_applications",
                    "purpose": "Confirm user is assigned to the application"
                },
                {
                    "step": "check_sso_logs",
                    "tool": "get_application_logs",
                    "purpose": "Look for SSO errors and authentication issues",
                    "timeframe": "24 hours"
                },
                {
                    "step": "check_app_errors",
                    "tool": "search_logs",
                    "purpose": "Find application-specific error events"
                }
            ],
            "common_solutions": [
                {"issue": "NOT_ASSIGNED", "action": "request_app_assignment"},
                {"issue": "APP_INACTIVE", "action": "contact_app_admin"},
                {"issue": "SSO_CONFIG_ERROR", "action": "escalate_to_technical"},
                {"issue": "PERMISSION_DENIED", "action": "check_group_memberships"}
            ]
        },

        "account_disabled": {
            "description": "User account has been disabled or deprovisioned",
            "investigation_steps": [
                {
                    "step": "check_lifecycle_events",
                    "tool": "search_logs",
                    "query": "eventType sw \"user.lifecycle\" and target.alternateId eq \"{user_email}\"",
                    "purpose": "Find when and why account was disabled"
                },
                {
                    "step": "check_admin_actions",
                    "tool": "search_logs",
                    "query": "target.alternateId eq \"{user_email}\" and actor.type eq \"User\"",
                    "purpose": "Identify which admin made changes"
                },
                {
                    "step": "check_policy_violations",
                    "tool": "search_logs",
                    "purpose": "Look for policy-based automatic actions"
                }
            ],
            "escalation_required": True,
            "next_steps": [
                "Contact manager or HR for reactivation approval",
                "Verify employment status",
                "Check compliance requirements"
            ]
        }
    }


def get_response_templates() -> Dict[str, str]:
    """Get response templates for common scenarios.

    Returns:
        Dictionary of response templates
    """
    return {
        "investigation_start": "Let me investigate this {issue_type} for you. I'll check your account status and recent activity to identify the root cause...",

        "account_locked": """I found that your account is locked out due to {lockout_reason}.

This happened at {lockout_time} after {failed_attempts} failed login attempts.

I can unlock your account immediately. Would you like me to do that now?""",

        "password_expired": """Your password expired on {expiration_date} according to your organization's password policy.

I can send you a password reset email so you can set a new password. Would you like me to do that?""",

        "app_not_assigned": """I found the issue: You're not currently assigned to the {app_name} application.

Looking at the logs, I can see your access was {action} on {date} by {admin}.

I can request {app_name} access for you, but this will need approval from your manager. Would you like me to start that process?""",

        "technical_issue": """I've identified a technical issue with {component}: {error_description}

This requires attention from our technical team. I've documented the details and will escalate this for resolution.

In the meantime, you can try: {workaround_steps}""",

        "resolution_success": """✅ Resolved! I've successfully {action_taken}.

{verification_message}

To prevent this issue in the future:
{prevention_tips}

Is there anything else I can help you with?""",

        "escalation_needed": """This issue requires escalation to {team} because {reason}.

I've documented all the investigation details:
{summary}

Expected resolution time: {timeline}
Reference number: {ticket_id}

I'll follow up with you once this is resolved."""
    }


def format_prompt_with_context(template: str, context: Dict[str, Any]) -> str:
    """Format a prompt template with context variables.

    Args:
        template: The prompt template with placeholders
        context: Dictionary of context variables to substitute

    Returns:
        Formatted prompt string
    """
    try:
        return template.format(**context)
    except KeyError as e:
        # Handle missing context variables gracefully
        return template.replace(f"{{{e.args[0]}}}", f"[{e.args[0]} not available]")


def get_help_prompts() -> Dict[str, str]:
    """Get help and guidance prompts for users.

    Returns:
        Dictionary of help prompts
    """
    return {
        "available_commands": """I can help you with various Okta issues:

🔐 **Login Problems**: Account locked, password issues, MFA problems
📱 **App Access**: Can't access applications, SSO errors, missing apps
👤 **Account Issues**: Profile updates, reactivation, permission questions
📊 **Activity Review**: Check recent activity, security alerts, login history

What specific issue are you experiencing?""",

        "capabilities_overview": """I have access to comprehensive Okta management tools:

✅ **Investigate**: Check account status, review logs, analyze patterns
✅ **Diagnose**: Identify root causes through systematic analysis
✅ **Resolve**: Unlock accounts, reset passwords, update profiles
✅ **Monitor**: Search security events, track user activity

Just describe your issue in plain language and I'll handle the technical investigation.""",

        "privacy_notice": """🔒 **Privacy & Security Notice**:
- I only access information necessary to resolve your issue
- I'll ask for your confirmation before making any changes
- All actions are logged for security and audit purposes
- I follow least-privilege principles for account access"""
    }