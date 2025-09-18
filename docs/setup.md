# Setup Guide

## Prerequisites

Before installing MCP Okta Support, ensure you have:

- **Python 3.9 or higher**
- **Okta organization** with administrative access
- **Local LLM environment** (Ollama, gpt-oss, or Claude Desktop)

## 1. Installation

### Option A: Standard Python Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-okta-support

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Option B: Docker Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-okta-support

# Build and start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## 2. Okta Configuration

### 2.1 API Token Setup (Easier)

1. **Log into Okta Admin Console**
   - Navigate to your Okta organization: `https://your-org.okta.com`
   - Sign in with administrator credentials

2. **Create API Token**
   - Go to **Security > API**
   - Click **Create Token**
   - Enter a descriptive name (e.g., "MCP Okta Support")
   - Click **Create Token**
   - **Important**: Copy the token immediately (it won't be shown again)

3. **Set Required Permissions**
   - API tokens inherit the permissions of the admin user who created them
   - Ensure your admin account has:
     - User management permissions
     - Application management permissions
     - System log access

### 2.2 OAuth 2.0 Setup (Recommended for Production)

1. **Create Service Application**
   - Go to **Applications > Applications**
   - Click **Create App Integration**
   - Select **API Services**
   - Click **Next**

2. **Configure Application**
   - **App integration name**: "MCP Okta Support"
   - Click **Save**

3. **Note Credentials**
   - Copy the **Client ID**
   - Copy the **Client Secret**

4. **Grant Scopes**
   - Go to **Security > API**
   - Click **Authorization Servers**
   - Select your authorization server
   - Go to **Scopes** tab
   - Ensure these scopes exist and are granted:
     - `okta.users.manage`
     - `okta.apps.manage`
     - `okta.logs.read`

## 3. Environment Configuration

### 3.1 Create Environment File

```bash
# Copy the example environment file
cp .env.example .env
```

### 3.2 Configure API Token Method

Edit `.env` file:

```bash
# Required
OKTA_ORG_URL=https://your-org.okta.com
OKTA_API_TOKEN=your_api_token_here

# Optional
MCP_SERVER_NAME=okta-support
MCP_LOG_LEVEL=INFO
OKTA_RATE_LIMIT=100
OKTA_TIMEOUT_SECONDS=30
DEVELOPMENT_MODE=false
LOG_STRUCTURED=true
```

### 3.3 Configure OAuth 2.0 Method

Edit `.env` file:

```bash
# Required
OKTA_ORG_URL=https://your-org.okta.com
OKTA_CLIENT_ID=your_client_id
OKTA_CLIENT_SECRET=your_client_secret
OKTA_SCOPES=okta.users.manage,okta.apps.manage,okta.logs.read

# Optional
MCP_SERVER_NAME=okta-support
MCP_LOG_LEVEL=INFO
OKTA_RATE_LIMIT=100
OKTA_TIMEOUT_SECONDS=30
DEVELOPMENT_MODE=false
LOG_STRUCTURED=true
```

## 4. Verify Configuration

### 4.1 Test Okta Connectivity

```bash
# Test with API Token
curl -H "Authorization: SSWS your_api_token" \
     https://your-org.okta.com/api/v1/users/me

# Test with OAuth (requires token exchange)
curl -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&scope=okta.users.read" \
     -u "client_id:client_secret" \
     https://your-org.okta.com/oauth2/default/v1/token
```

### 4.2 Start MCP Server

```bash
# Start the server
python -m mcp_okta_support.main

# You should see output like:
# INFO: Starting MCP Okta Support server
# INFO: Okta org: https://your-org.okta.com
# INFO: Authentication method: api_token (or oauth)
# INFO: MCP server setup completed successfully
```

## 5. LLM Integration

### 5.1 Claude Desktop Integration

1. **Locate Configuration File**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add MCP Server Configuration**

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
  }
}
```

3. **Restart Claude Desktop**

4. **Test Connection**
   - Open Claude Desktop
   - Try a command like: "List the first 5 users in our Okta organization"

### 5.2 Ollama Integration

1. **Install MCP Client for Ollama**
   ```bash
   # Install MCP client (implementation varies by setup)
   pip install mcp-client-ollama  # Example package name
   ```

2. **Configure Connection**
   ```bash
   # Start MCP server in one terminal
   python -m mcp_okta_support.main

   # In another terminal, start Ollama with MCP
   ollama run llama2 --mcp-server http://localhost:8000
   ```

### 5.3 Custom LLM Integration

For other LLM environments, implement MCP client following the [MCP specification](https://modelcontextprotocol.io/docs/).

## 6. Verification and Testing

### 6.1 Test Basic Functionality

1. **Server Health Check**
   ```bash
   # Check if server is running
   python -c "import mcp_okta_support; print('Import successful')"
   ```

2. **Test User Operations**
   - Try: "Get details for the first user in our organization"
   - Try: "Show me my user information"

3. **Test Application Operations**
   - Try: "List all applications"
   - Try: "Show me details for the first application"

4. **Test Log Operations**
   - Try: "Show me recent login failures"
   - Try: "Get logs from the last hour"

### 6.2 Troubleshooting Common Issues

#### Authentication Errors
```bash
# Verify token format
echo $OKTA_API_TOKEN | wc -c  # Should be ~40 characters

# Test API access
curl -v -H "Authorization: SSWS $OKTA_API_TOKEN" \
     https://your-org.okta.com/api/v1/users/me
```

#### Connection Issues
```bash
# Test network connectivity
ping your-org.okta.com
curl -I https://your-org.okta.com

# Check firewall/proxy settings
export https_proxy=http://proxy:port  # If behind proxy
```

#### Permission Issues
- Verify admin account has required permissions
- Check Okta API rate limits
- Review Okta system log for denied requests

## 7. Production Setup Considerations

### 7.1 Security

- **Never commit `.env` files** to version control
- **Use secrets management** in production (Vault, K8s secrets)
- **Rotate API tokens** regularly
- **Monitor API usage** for anomalies

### 7.2 Monitoring

```bash
# Enable structured logging for production
LOG_STRUCTURED=true
MCP_LOG_LEVEL=INFO

# Optional: Export logs to monitoring system
# Configure your log aggregation tool to parse JSON logs
```

### 7.3 Performance

```bash
# Adjust rate limits based on your Okta plan
OKTA_RATE_LIMIT=200  # Increase if you have higher limits

# Tune timeouts for your network
OKTA_TIMEOUT_SECONDS=60  # Increase for slower networks
```

### 7.4 High Availability

- **Multiple instances**: Run multiple MCP server instances
- **Load balancing**: Use load balancer if needed
- **Health checks**: Implement health monitoring
- **Graceful shutdown**: Handle SIGTERM signals

## 8. Development Setup

### 8.1 Development Dependencies

```bash
# Install development dependencies
pip install -e ".[dev]"

# This includes:
# - pytest (testing)
# - black (formatting)
# - ruff (linting)
# - mypy (type checking)
```

### 8.2 Development Environment

```bash
# Enable development mode
export DEVELOPMENT_MODE=true
export MCP_LOG_LEVEL=DEBUG

# Start with auto-reload (if using uvicorn)
python -m mcp_okta_support.main --reload
```

### 8.3 Pre-commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 9. Next Steps

After successful setup:

1. **Read the [Usage Guide](usage.md)** for detailed command examples
2. **Review [Architecture Documentation](architecture.md)** to understand the system
3. **Check [Troubleshooting Guide](troubleshooting.md)** for common issues
4. **Explore example queries** in the examples directory

## Support

If you encounter issues during setup:

1. **Check logs** for error messages
2. **Verify environment variables** are set correctly
3. **Test Okta connectivity** independently
4. **Review [Troubleshooting Guide](troubleshooting.md)**
5. **Open an issue** with detailed error information