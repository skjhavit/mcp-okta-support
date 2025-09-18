# Intelligent Okta Support Agent

This document explains how the MCP Okta Support system transforms your local LLM into an intelligent Okta support agent with expert troubleshooting capabilities.

## What Makes This Intelligent

Unlike simple API wrappers, this system provides your LLM with:

### 🧠 **Expert Knowledge**
- Comprehensive understanding of Okta architecture and common issues
- Proven troubleshooting methodologies used by real support professionals
- Knowledge of security best practices and compliance requirements

### 🔍 **Systematic Investigation Process**
- Structured approach to problem-solving
- Evidence-based diagnosis rather than guessing
- Root cause analysis that goes beyond surface symptoms

### 🛡️ **Security-First Mindset**
- Automatically identifies potential security threats
- Takes protective action when necessary
- Follows principle of least privilege

### 💬 **Human-Like Communication**
- Explains technical concepts in user-friendly language
- Asks clarifying questions when needed
- Provides clear next steps and preventive guidance

## The Intelligence Framework

### Core System Prompt

The system includes a comprehensive prompt that gives the LLM:

1. **Role Definition**: "You are an expert Okta Support Agent"
2. **Methodology**: Step-by-step troubleshooting approach
3. **Tool Usage**: How and when to use each MCP tool
4. **Communication Style**: How to interact with users
5. **Security Guidelines**: When to escalate or take protective action

### Troubleshooting Workflows

Pre-defined workflows for common scenarios:

```
Login Issues:
1. Check user account status
2. Review recent login attempts
3. Analyze failed login patterns
4. Identify root cause
5. Propose and execute solution
6. Verify resolution
```

### Response Templates

Structured templates for consistent communication:

```
"I found the issue: [ROOT CAUSE]
Here's what happened: [EXPLANATION]
I can fix this by [PROPOSED ACTION]
Would you like me to proceed?"
```

## How It Works in Practice

### Traditional Approach (Without Intelligence)
```
User: "I can't login"
System: [Runs get_user_details()]
Response: "Here's your user data: {JSON dump}"
User: [Still confused, doesn't know what the data means]
```

### Intelligent Agent Approach
```
User: "I can't login"

Agent: "Let me investigate this login issue for you..."
[Strategically calls multiple tools to build complete picture]

Agent: "I found that your account is LOCKED_OUT due to 5 failed
login attempts this morning at 9:15 AM. This typically happens
when the wrong password is entered multiple times.

Looking at the source IP addresses, they all came from your
usual office location, so this appears to be a password issue
rather than a security threat.

I can unlock your account immediately. Would you like me to do that?"

[After user confirms]

Agent: "✅ Done! Your account is unlocked. To prevent this in
the future, consider using a password manager if you're unsure
about your current password."
```

## Key Capabilities

### 1. **Multi-Tool Orchestration**
The agent knows how to combine multiple tools strategically:

```python
# Instead of just calling one tool:
get_user_details(user)

# The agent orchestrates multiple tools:
user_info = get_user_details(user)
if user_info.status == "LOCKED_OUT":
    recent_logs = get_user_logs(user, since="24 hours")
    failed_attempts = get_failed_login_attempts(since="24 hours")
    # Analyze patterns, identify cause, propose solution
```

### 2. **Context-Aware Decision Making**
The agent makes intelligent decisions based on evidence:

```
IF account_status == "LOCKED_OUT" AND failed_attempts > 3:
    → Likely password issue, offer unlock

IF account_status == "DEPROVISIONED" AND admin_action_found:
    → Policy/HR issue, escalate appropriately

IF sso_errors AND app_config_changed_recently:
    → Technical issue, provide workarounds
```

### 3. **Progressive Investigation**
Starts with basic checks and deepens investigation as needed:

```
Level 1: Quick status check
Level 2: Recent activity analysis
Level 3: Deep log investigation
Level 4: Cross-system correlation
Level 5: Security threat analysis
```

### 4. **User Experience Focus**
Always prioritizes user understanding and consent:

- Explains findings in plain language
- Asks permission before making changes
- Provides preventive guidance
- Offers multiple solution options

## Advanced Features

### Security Threat Detection
```
Agent: "I found concerning activity: 3 login attempts from
different countries in the past 24 hours, plus 2 MFA bypass
attempts. This suggests someone may have your credentials.

This is a security emergency. I need to:
1. Reset your password immediately
2. Enable additional monitoring
3. Review your email for unauthorized access

Would you like me to secure your account right now?"
```

### Proactive Problem Solving
```
Agent: "I've fixed your login issue, but I also noticed your
password is 180 days old, which violates our 90-day policy.
Your account might be locked again soon.

Would you like me to send you a password reset link so you
can update it proactively?"
```

### Complex Scenario Handling
```
Agent: "I found multiple issues affecting your experience:

1. Your account was recently migrated (causing SSO issues)
2. Your group membership changed (affecting app access)
3. There's ongoing system maintenance (causing slowdowns)

Let me address these in priority order..."
```

## Configuration Options

### Basic Configuration
Minimal setup for basic functionality:
```json
{
  "customInstructions": "You are an Okta support agent. Always investigate systematically and ask for permission before making changes."
}
```

### Advanced Configuration
Full intelligent agent with detailed methodology:
```json
{
  "customInstructions": "[Complete system prompt from prompts/system_prompt.md]"
}
```

### Custom Workflows
Organization-specific troubleshooting procedures:
```json
{
  "customInstructions": "[Standard prompt] + [Custom workflows for your org]"
}
```

## Measuring Intelligence

The system demonstrates intelligence through:

### ✅ **Systematic Approach**
- Follows logical investigation steps
- Doesn't jump to conclusions
- Builds evidence-based diagnosis

### ✅ **Contextual Understanding**
- Recognizes patterns and relationships
- Considers multiple potential causes
- Adapts approach based on findings

### ✅ **Proactive Behavior**
- Identifies related issues before they become problems
- Suggests preventive measures
- Offers additional assistance

### ✅ **Clear Communication**
- Explains technical concepts simply
- Provides actionable guidance
- Maintains professional, helpful tone

### ✅ **Security Awareness**
- Recognizes potential threats
- Takes appropriate protective action
- Follows compliance requirements

## Getting Started

1. **Use the enhanced Claude Desktop configuration** from `examples/claude_desktop_config_with_prompt.json`
2. **Review the system prompt** in `src/mcp_okta_support/prompts/system_prompt.md`
3. **Test with sample scenarios** from `examples/prompt_examples.md`
4. **Customize for your organization** by extending the base prompt

## The Result

Instead of a simple tool interface, you get a **knowledgeable colleague** who:

- Understands Okta deeply
- Investigates problems systematically
- Communicates clearly and professionally
- Prioritizes security and user experience
- Continuously learns and improves

This transforms routine support tasks into intelligent, efficient problem-solving sessions that actually resolve issues rather than just providing data.