# MCP Okta Support

A Model Context Protocol (MCP) server that enables local LLMs to perform Okta user and application management tasks through natural language commands.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd mcp-okta-support

# Install dependencies
pip install -r requirements.txt

# Configure your Okta credentials
cp .env.example .env
# Edit .env with your Okta organization details

# Start the MCP server
python -m mcp_okta_support.main
```

## 📋 Prerequisites

- Python 3.9 or higher
- Okta organization with API access
- Local LLM (Ollama, gpt-oss, or Claude Desktop)

## 🔧 Installation

### Option 1: Standard Installation

```bash
# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Option 2: Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Okta Organization
OKTA_ORG_URL=https://your-org.okta.com

# Option 1: API Token (simpler setup)
OKTA_API_TOKEN=your_api_token_here

# Option 2: OAuth 2.0 (recommended for production)
OKTA_CLIENT_ID=your_client_id
OKTA_CLIENT_SECRET=your_client_secret
OKTA_SCOPES=okta.users.manage,okta.apps.manage,okta.logs.read

# Optional: Server Configuration
MCP_SERVER_NAME=okta-support
MCP_LOG_LEVEL=INFO
OKTA_RATE_LIMIT=100
OKTA_TIMEOUT_SECONDS=30
```

### Okta API Credentials Setup

#### Option 1: API Token
1. Log into your Okta admin console
2. Go to **Security > API**
3. Create a new API token
4. Copy the token to your `.env` file

#### Option 2: OAuth 2.0 (Recommended)
1. Go to **Applications > Applications** in Okta admin
2. Create a new **API Services** application
3. Note the Client ID and Client Secret
4. Grant required scopes:
   - `okta.users.manage` - User management operations
   - `okta.apps.manage` - Application management
   - `okta.logs.read` - System log access

## 🎯 Usage Examples

### Connect to Local LLM

#### With Claude Desktop (Recommended Configuration)
Add to your Claude Desktop configuration file:

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration with Intelligent Support Agent:**
```json
{
  "mcpServers": {
    "okta-support": {
      "command": "python",
      "args": ["-m", "mcp_okta_support.main"],
      "env": {
        "OKTA_ORG_URL": "https://your-org.okta.com",
        "OKTA_API_TOKEN": "your_token"
      }
    }
  },
  "customInstructions": "You are an expert Okta Support Agent. Always investigate issues systematically: 1) Check user account status with get_user_details() 2) Review recent activity with get_user_logs() 3) Search for specific errors with search_logs() 4) Diagnose root cause 5) Ask for permission before making changes 6) Verify resolution. For login issues: check if account is locked, look for failed attempts, identify cause. For app access: verify user assignments and check SSO logs. Always explain your findings clearly and offer solutions."
}
```

**Why This Configuration:**
- **Intelligent Agent**: The `customInstructions` field turns Claude into an expert Okta troubleshooter
- **Systematic Approach**: Follows proven investigation methodology
- **User Safety**: Always asks permission before making changes
- **Root Cause Focus**: Doesn't just fix symptoms, finds underlying issues

#### With Ollama
```bash
# Start the MCP server
python -m mcp_okta_support.main

# In another terminal, connect your Ollama model
# (Integration details depend on your Ollama MCP client setup)
```

### Intelligent Support Examples

Once connected, you get an **intelligent Okta support agent** that investigates issues systematically:

#### Real Support Scenarios

**🔐 Login Issues:**
```
You: "I can't login to Okta"

Agent: "Let me investigate this login issue for you. First, let me check your account status..."
[Automatically calls get_user_details()]

Agent: "I found that your account is LOCKED_OUT due to 5 failed login attempts this morning.
Looking at the logs, they all came from your usual location, so this appears to be a
password issue rather than a security threat.

I can unlock your account immediately. Would you like me to do that now?"

You: "Yes please"

Agent: "✅ Done! Your account is now unlocked. You should be able to login normally.
To prevent this, consider using a password manager if you're unsure about your current password."
```

**📱 App Access Issues:**
```
You: "I can't access Salesforce anymore"

Agent: "Let me troubleshoot Salesforce access for you..."
[Checks user status, app assignments, and SSO logs]

Agent: "I found the issue: You're not currently assigned to the Salesforce application.
Looking at the logs, your access was removed 3 days ago by Jane Smith.

I can request Salesforce access for you, but this will need approval from your manager.
Would you like me to start that process?"
```

**🔍 Complex Investigation:**
```
You: "I keep getting weird security alerts"

Agent: "Let me do a comprehensive security review..."
[Analyzes user logs, security events, and patterns]

Agent: "I found concerning activity: 3 login attempts from unusual locations and
2 MFA bypass attempts in the past week. This suggests someone may have your credentials.

I need to secure your account immediately. I can:
1. Reset your password right now
2. Enable additional security monitoring
3. Review your recent email for unauthorized reset requests

This is urgent - would you like me to proceed with securing your account?"
```

#### Why This Is Powerful

- **🧠 Intelligent Investigation**: Doesn't just run commands - actually investigates like a human expert
- **🔍 Root Cause Analysis**: Finds WHY things are broken, not just WHAT is broken
- **🛡️ Security First**: Identifies threats and takes protective action
- **✅ User Consent**: Always asks permission before making changes
- **📋 Clear Explanations**: Explains technical issues in simple terms
- **🎯 End-to-End Resolution**: Doesn't stop until the issue is fully resolved

## 🛠️ Available Tools

### User Management
- **get_user_details** - Retrieve user information
- **update_user_profile** - Update user profile attributes
- **reinvite_user** - Re-send user invitation
- **unlock_user_account** - Unlock locked accounts
- **reset_user_password** - Initiate password reset

### Application Management
- **list_applications** - List organization applications
- **get_application_details** - Get app configuration
- **update_application_config** - Update app settings

### System Logs
- **get_user_logs** - User activity logs
- **get_application_logs** - App-specific logs
- **search_logs** - Search with custom queries

## 📖 Documentation

- [Architecture Overview](docs/architecture.md)
- [Setup Guide](docs/setup.md)
- [Usage Examples](docs/usage.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🧪 Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_okta_support

# Run specific test file
pytest tests/test_okta_client.py
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Development Mode
```bash
# Start in development mode with debug logging
DEVELOPMENT_MODE=true MCP_LOG_LEVEL=DEBUG python -m mcp_okta_support.main
```

## 🔒 Security Considerations

- **API Credentials**: Store credentials securely, never commit to version control
- **Rate Limiting**: Built-in rate limiting prevents API abuse
- **Input Validation**: All inputs are validated before API calls
- **Error Handling**: Sensitive information is not exposed in error messages
- **Logging**: Structured logging for audit and debugging

## 🚨 Troubleshooting

### Common Issues

**Authentication Failed**
```bash
# Verify your credentials
curl -H "Authorization: SSWS your_token" https://your-org.okta.com/api/v1/users/me
```

**Rate Limiting**
- The server automatically handles rate limits
- Increase `OKTA_RATE_LIMIT` if needed
- Monitor logs for rate limit warnings

**Connection Issues**
- Verify `OKTA_ORG_URL` format
- Check network connectivity
- Review firewall/proxy settings

See [Troubleshooting Guide](docs/troubleshooting.md) for detailed solutions.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/your-org/mcp-okta-support/issues)
- 💬 [Discussions](https://github.com/your-org/mcp-okta-support/discussions)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local LLM     │    │   MCP Client    │    │   MCP Server    │
│ (Ollama/Claude) │◄──►│   (Protocol)    │◄──►│  (This Project) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Okta APIs     │
                                               │ - Users API     │
                                               │ - Apps API      │
                                               │ - System Logs   │
                                               └─────────────────┘
```

---

**Built with ❤️ for the MCP community**