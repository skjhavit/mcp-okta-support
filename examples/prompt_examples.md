# Okta Support Agent - Prompt Examples

This document shows how the intelligent Okta Support Agent prompt works in practice with real user scenarios.

## Example 1: Login Issue

### User Query
> "I can't login to Okta"

### Agent Response (Following the System Prompt)
```
Let me investigate this login issue for you. First, let me check your account status...

[Calls get_user_details("user@company.com")]

I can see your account status is LOCKED_OUT. Let me check what caused this by looking at recent login attempts...

[Calls get_user_logs() and get_failed_login_attempts()]

I found the issue: Your account was locked after 5 failed login attempts this morning at 9:15 AM. This typically happens when:
- Wrong password is entered multiple times
- Someone else might be trying to access your account
- Your password may have been changed recently

Looking at the failed attempts, they all came from your usual location, so this appears to be a password issue rather than a security threat.

I can unlock your account immediately. Would you like me to do that now?

[User confirms]

✅ Done! Your account is now unlocked. You should be able to login normally.

To prevent this in the future:
- Make sure you're using your current password
- If you're unsure, I can send you a password reset link
- Consider using a password manager

Is there anything else I can help you with?
```

## Example 2: Application Access Issue

### User Query
> "I can't access Salesforce anymore"

### Agent Response
```
Let me help you troubleshoot Salesforce access. First, let me check your account and then look at your application assignments...

[Calls get_user_details() then get_application_details("Salesforce")]

I can see your Okta account is ACTIVE, and Salesforce is also active in our system. Let me check if you're assigned to the Salesforce application and look at recent access logs...

[Calls get_application_logs("Salesforce") and searches for user's SSO attempts]

I found the issue: You're not currently assigned to the Salesforce application. Looking at the system logs, I can see your access was removed 3 days ago on January 15th at 2:30 PM by Jane Smith (jane.smith@company.com).

This was likely due to:
- Team restructuring
- Role changes
- License optimization
- Compliance requirements

I have a few options to help you:

1. **Request new access**: I can initiate a Salesforce access request, but this will need approval from your manager
2. **Contact your manager**: You might want to discuss this directly with your manager first
3. **Check with Jane Smith**: Since she removed the access, she might have context about why

Which approach would you prefer? I can start the access request process if you'd like.
```

## Example 3: Complex Investigation

### User Query
> "I keep getting weird security alerts and my apps are loading slowly"

### Agent Response
```
Let me investigate these security alerts and performance issues for you. This requires a comprehensive review, so I'll check several areas...

[Calls get_user_details()]

Your account status is ACTIVE, which is good. Now let me examine your recent activity and look for any unusual patterns...

[Calls get_user_logs(since="7 days ago") and search_logs for security events]

I found several concerning events:

**Security Alerts (Past 7 Days):**
- 3 login attempts from unusual locations (IP addresses in different countries)
- 2 MFA bypass attempts
- 1 password reset request you didn't initiate

**Performance Issues:**
- 12 SSO timeout errors across different applications
- Multiple session refreshes indicating connectivity problems

**Root Cause Analysis:**
1. **Security Issue**: Someone may have your credentials and is trying to access your account
2. **Performance Issue**: The security measures are causing additional verification steps, slowing down app access

**Immediate Actions Needed:**
1. Reset your password immediately
2. Review and update your MFA settings
3. Check for any unauthorized access to your email

I can start the password reset process right now and help secure your account. This is urgent - would you like me to proceed immediately?

[After user confirms]

✅ Sending password reset email now...
✅ I'm also enabling additional security monitoring on your account...

**Next Steps:**
1. Change your password when you receive the email
2. Update passwords on any other accounts that use the same password
3. Review your recent email for any suspicious password reset requests
4. Contact our security team at security@company.com to report the unauthorized attempts

I'll follow up with you in 24 hours to ensure everything is working properly. This is a security priority, so please complete the password reset as soon as possible.
```

## Example 4: Proactive Troubleshooting

### User Query
> "My manager said my account was disabled"

### Agent Response
```
Let me investigate what happened with your account. I'll check the user lifecycle events to understand when and why it was disabled...

[Calls search_logs for user lifecycle events and admin actions]

I found the account status change details:

**Account Status:** DEPROVISIONED
**When:** Yesterday (January 16th) at 4:45 PM
**Who:** System automation (triggered by HR system integration)
**Reason:** Employee status change in HR system

Looking deeper into the timeline:

[Calls search_logs for related HR system events]

**What Happened:**
1. Your employment status was updated in the HR system at 4:30 PM
2. Our automated system detected this change 15 minutes later
3. Your Okta account was automatically deprovisioned per company policy
4. All application access was revoked as a security measure

This appears to be an HR system integration issue rather than a manual administrative action.

**To Resolve This:**
1. **Verify with HR**: Confirm your employment status in their system
2. **Manager Confirmation**: Your manager needs to verify this was an error
3. **Reactivation Process**: Once confirmed, I can work with HR to restore your access

**Important:** I cannot reactivate your account directly as this requires HR approval for compliance reasons.

**Next Steps:**
1. Contact HR immediately to verify your status
2. Ask your manager to confirm with HR that you should remain active
3. Once HR confirms, they can trigger the reactivation process
4. I can monitor for the reactivation and help restore your application access

**Reference Information:**
- Deactivation Event ID: EVT-2024-0116-4567
- HR System Reference: HR-CHG-789123
- Expected Resolution Time: 2-4 hours after HR confirmation

Would you like me to help you draft an email to HR with the technical details they'll need?
```

## Example 5: Multi-Issue Investigation

### User Query
> "Nothing is working right today - can't login, apps are broken, getting error messages"

### Agent Response
```
That sounds frustrating! Let me do a comprehensive investigation to identify all the issues and their connections. Multiple problems often have a common root cause...

[Performs systematic investigation across multiple areas]

**Step 1: Account Status Check**
[Calls get_user_details()]
✅ Account is ACTIVE - not a basic account issue

**Step 2: Recent Activity Analysis**
[Calls get_user_logs(since="24 hours ago")]
🔍 Found 15 error events in the past 24 hours - investigating patterns...

**Step 3: System-Wide Issues Check**
[Calls search_logs for system events and outages]
🎯 **Found the root cause!**

**What's Happening:**
There's an ongoing system maintenance affecting authentication services that started at 8:00 AM today. This is causing:

1. **Intermittent login failures** (authentication service slowdown)
2. **Application loading issues** (SSO timeouts)
3. **Error messages** (service retry attempts)

**Current Status:**
- Maintenance Window: 8:00 AM - 12:00 PM today
- Affected Services: Primary authentication, SSO processing
- Progress: 75% complete (estimated completion: 11:30 AM)

**Immediate Workarounds:**
1. **For Login**: Try logging in again in 5-10 minutes if it fails
2. **For Apps**: Use direct login URLs where available (I can provide these)
3. **Browser**: Clear cache and cookies if you continue having issues

**Direct App Access URLs:**
- Salesforce: [provides direct URL]
- Office 365: [provides direct URL]
- Slack: [provides direct URL]

**Good News:**
- This is temporary and should resolve completely by 11:30 AM
- No action needed on your part
- Your account and data are completely secure

**I'll Monitor For You:**
- Checking every 15 minutes for service restoration
- Will notify you when maintenance is complete
- Can provide additional workarounds if needed

This isn't a problem with your account - it's a planned system improvement that's taking a bit longer than expected. Everything should be back to normal very soon!

Would you like me to show you how to access any specific applications directly while we wait for the maintenance to complete?
```

## Key Features Demonstrated

### 1. **Systematic Investigation**
- Always starts with basic checks
- Follows logical progression
- Uses multiple tools to gather evidence
- Connects related events

### 2. **Root Cause Analysis**
- Doesn't stop at symptoms
- Looks for underlying causes
- Considers system-wide issues
- Analyzes patterns and timelines

### 3. **Clear Communication**
- Explains technical issues in simple terms
- Provides step-by-step findings
- Offers multiple solution options
- Sets clear expectations

### 4. **Proactive Support**
- Anticipates follow-up questions
- Provides preventive guidance
- Offers additional assistance
- Monitors for resolution

### 5. **Security Awareness**
- Identifies security threats
- Takes immediate protective action
- Follows compliance requirements
- Escalates appropriately

### 6. **User Consent**
- Always asks before making changes
- Explains what actions will be taken
- Provides options and alternatives
- Respects user preferences

This intelligent prompt framework ensures every user interaction is thorough, helpful, and professional while maintaining the highest security standards.