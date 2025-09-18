# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with MCP Okta Support.

## Quick Diagnostic Commands

Before diving into specific issues, run these quick tests:

```bash
# Test Python environment
python --version  # Should be 3.9+
python -c "import mcp_okta_support; print('✓ Package imports successfully')"

# Test configuration
python -c "from mcp_okta_support.config import Settings; s=Settings(); print('✓ Configuration loaded')"

# Test Okta connectivity
curl -H "Authorization: SSWS $OKTA_API_TOKEN" https://your-org.okta.com/api/v1/users/me
```

## Authentication Issues

### Problem: "Authentication failed" or 401 errors

#### Symptoms
- Error messages about invalid credentials
- HTTP 401 responses from Okta API
- "SSWS token not found" errors

#### Solutions

**1. Verify API Token Format**
```bash
# Check token length (should be ~40 characters)
echo $OKTA_API_TOKEN | wc -c

# Check token doesn't have extra whitespace
echo "'$OKTA_API_TOKEN'" | cat -A
```

**2. Test Token Manually**
```bash
# Test with curl
curl -v -H "Authorization: SSWS $OKTA_API_TOKEN" \
     https://your-org.okta.com/api/v1/users/me

# Expected response: User information
# Error response: Check token validity
```

**3. Verify Environment Variables**
```bash
# Check if variables are set
env | grep OKTA

# Reload environment file
source .env  # or restart your terminal
```

**4. Token Regeneration**
- Log into Okta admin console
- Go to Security > API
- Revoke old token and create new one
- Update `.env` file with new token

### Problem: OAuth 2.0 authentication failures

#### Symptoms
- "Invalid client credentials" errors
- OAuth token exchange failures
- 400 errors during authentication

#### Solutions

**1. Verify OAuth Configuration**
```bash
# Check client credentials are set
echo "Client ID: $OKTA_CLIENT_ID"
echo "Client Secret: $OKTA_CLIENT_SECRET"
echo "Scopes: $OKTA_SCOPES"
```

**2. Test OAuth Token Exchange**
```bash
# Test client credentials flow
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&scope=okta.users.read" \
  -u "$OKTA_CLIENT_ID:$OKTA_CLIENT_SECRET" \
  https://your-org.okta.com/oauth2/default/v1/token
```

**3. Verify Application Configuration**
- Check application exists in Okta admin
- Verify "API Services" application type
- Confirm granted scopes match your needs

## Connection Issues

### Problem: Network connectivity errors

#### Symptoms
- Timeout errors
- "Connection refused" messages
- DNS resolution failures

#### Solutions

**1. Test Basic Connectivity**
```bash
# Test DNS resolution
nslookup your-org.okta.com

# Test HTTPS connectivity
curl -I https://your-org.okta.com

# Test with verbose output
curl -v https://your-org.okta.com/api/v1/users/me
```

**2. Check Proxy Settings**
```bash
# If behind corporate proxy
export https_proxy=http://proxy.company.com:8080
export http_proxy=http://proxy.company.com:8080

# Test with proxy
curl --proxy $https_proxy https://your-org.okta.com
```

**3. Firewall and Security**
- Verify outbound HTTPS (port 443) is allowed
- Check if corporate firewall blocks Okta domains
- Whitelist `*.okta.com` and `*.oktapreview.com`

### Problem: SSL/TLS certificate errors

#### Symptoms
- "SSL certificate verify failed" errors
- Certificate validation warnings

#### Solutions

**1. Update CA Certificates**
```bash
# On Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates

# On macOS
brew install ca-certificates

# On Windows
# Update Windows certificates via Windows Update
```

**2. Check Certificate Chain**
```bash
# Test SSL connection
openssl s_client -connect your-org.okta.com:443 -servername your-org.okta.com

# Verify certificate validity
curl -vvI https://your-org.okta.com 2>&1 | grep -i cert
```

## Rate Limiting Issues

### Problem: "Rate limit exceeded" errors

#### Symptoms
- HTTP 429 responses
- "Too Many Requests" errors
- Automatic delays in responses

#### Solutions

**1. Check Current Rate Limit Status**
```bash
# View rate limit headers in response
curl -v -H "Authorization: SSWS $OKTA_API_TOKEN" \
     https://your-org.okta.com/api/v1/users/me 2>&1 | grep -i rate
```

**2. Adjust Rate Limiting Configuration**
```bash
# In .env file, reduce rate limit
OKTA_RATE_LIMIT=50  # Default is 100

# Increase timeout for slower responses
OKTA_TIMEOUT_SECONDS=60  # Default is 30
```

**3. Monitor API Usage**
- Check Okta admin console for API usage
- Review system logs for rate limit warnings
- Consider upgrading Okta plan for higher limits

### Problem: Requests timing out

#### Symptoms
- "Request timeout" errors
- Long delays before failures
- Partial responses

#### Solutions

**1. Increase Timeout Settings**
```bash
# In .env file
OKTA_TIMEOUT_SECONDS=60  # Increase from default 30
```

**2. Test Network Latency**
```bash
# Measure response time
time curl -H "Authorization: SSWS $OKTA_API_TOKEN" \
     https://your-org.okta.com/api/v1/users/me
```

**3. Optimize Queries**
- Use specific filters to reduce response size
- Limit result counts for large datasets
- Break large operations into smaller chunks

## Configuration Issues

### Problem: "Configuration error" on startup

#### Symptoms
- Validation errors during startup
- Missing required environment variables
- Invalid URL formats

#### Solutions

**1. Validate Environment File**
```bash
# Check .env file syntax
cat .env | grep -v '^#' | grep -v '^$'

# Test configuration loading
python -c "
from mcp_okta_support.config import Settings
try:
    s = Settings()
    print('✓ Configuration valid')
    print(f'Org URL: {s.okta_org_url}')
    print(f'Auth method: {\"oauth\" if s.is_oauth_configured else \"api_token\"}')
except Exception as e:
    print(f'✗ Configuration error: {e}')
"
```

**2. Fix Common Configuration Errors**

**Invalid URL Format**:
```bash
# Correct format
OKTA_ORG_URL=https://your-org.okta.com

# Incorrect formats
OKTA_ORG_URL=your-org.okta.com  # Missing https://
OKTA_ORG_URL=https://your-org.okta.com/  # Extra trailing slash
```

**Missing Required Variables**:
```bash
# Must have either API token OR OAuth credentials
OKTA_API_TOKEN=your_token  # OR
OKTA_CLIENT_ID=your_id
OKTA_CLIENT_SECRET=your_secret
```

### Problem: Permission denied errors

#### Symptoms
- HTTP 403 responses
- "Insufficient privileges" errors
- Access denied for specific operations

#### Solutions

**1. Verify Admin Permissions**
- Check if your admin account has required permissions
- Verify in Okta admin console under Security > Administrators

**2. Check API Token Scope**
- API tokens inherit permissions from the creating admin
- Recreate token with admin account that has broader permissions

**3. Verify OAuth Scopes**
```bash
# Required scopes for full functionality
OKTA_SCOPES=okta.users.manage,okta.apps.manage,okta.logs.read

# Check granted scopes in Okta admin console
```

## LLM Integration Issues

### Problem: LLM can't connect to MCP server

#### Symptoms
- "No MCP servers found" in LLM interface
- Connection timeout from LLM
- MCP tools not available

#### Solutions

**1. Verify MCP Server is Running**
```bash
# Check if server is running
ps aux | grep mcp_okta_support

# Check listening ports
netstat -an | grep 8000  # Or your configured port
```

**2. Test MCP Protocol**
```bash
# Start server with debug logging
MCP_LOG_LEVEL=DEBUG python -m mcp_okta_support.main

# Look for MCP protocol messages in logs
```

**3. Check LLM Configuration**

**Claude Desktop Configuration**:
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

### Problem: Tools not showing up in LLM

#### Symptoms
- MCP server connected but no tools available
- "Unknown tool" errors when trying commands
- Limited functionality available

#### Solutions

**1. Verify Tool Registration**
```bash
# Check server startup logs for tool registration
python -m mcp_okta_support.main 2>&1 | grep -i tool
```

**2. Test Tool Discovery**
```bash
# In LLM, try:
"What MCP tools are available?"
"List available Okta operations"
"Show me the MCP server capabilities"
```

**3. Restart LLM Application**
- Restart Claude Desktop or your LLM client
- Clear any cached MCP server information

## Performance Issues

### Problem: Slow response times

#### Symptoms
- Long delays for simple operations
- Timeouts on complex queries
- Unresponsive LLM interface

#### Solutions

**1. Enable Performance Logging**
```bash
# In .env file
MCP_LOG_LEVEL=DEBUG
LOG_STRUCTURED=true

# Monitor response times in logs
tail -f /path/to/logs | grep "response_time"
```

**2. Optimize Queries**
```bash
# Use specific filters instead of broad searches
"Get users in Engineering department"  # Better than "Get all users"

# Limit result counts
"Show me the first 10 applications"  # Better than "Show all applications"
```

**3. Check System Resources**
```bash
# Monitor CPU and memory usage
htop  # or top

# Check Python process resources
ps aux | grep python
```

## Logging and Debugging

### Enable Debug Logging

```bash
# In .env file
MCP_LOG_LEVEL=DEBUG
DEVELOPMENT_MODE=true
LOG_STRUCTURED=false  # For human-readable logs
```

### Structured Logging Analysis

```bash
# If using structured logging
tail -f logs/app.log | jq '.'  # Pretty print JSON logs

# Filter for errors
tail -f logs/app.log | jq 'select(.level == "error")'

# Filter for specific operations
tail -f logs/app.log | jq 'select(.function == "get_user_details")'
```

### Common Log Patterns

**Successful Operation**:
```json
{
  "timestamp": "2024-01-20T14:30:00Z",
  "level": "info",
  "message": "User retrieved successfully",
  "user_id": "00u1a2b3c4d5e6f7",
  "user_status": "ACTIVE"
}
```

**Error Pattern**:
```json
{
  "timestamp": "2024-01-20T14:30:00Z",
  "level": "error",
  "message": "Failed to get user details",
  "error": "User not found",
  "user_identifier": "invalid@example.com"
}
```

## Getting Help

### Collect Diagnostic Information

Before seeking help, collect this information:

```bash
# System information
python --version
pip list | grep -E "(fastmcp|httpx|pydantic)"

# Configuration (redacted)
python -c "
from mcp_okta_support.config import Settings
s = Settings()
print(f'Org URL: {s.okta_org_url}')
print(f'Auth: {\"oauth\" if s.is_oauth_configured else \"api_token\"}')
print(f'Rate limit: {s.okta_rate_limit}')
"

# Recent logs (last 50 lines)
tail -50 logs/app.log

# Network test results
curl -I https://your-org.okta.com
```

### Support Channels

1. **Check Documentation**
   - Review [Setup Guide](setup.md)
   - Check [Usage Examples](usage.md)
   - Read [Architecture Overview](architecture.md)

2. **Search Issues**
   - GitHub Issues: Common problems and solutions
   - Stack Overflow: Community solutions

3. **Create Support Request**
   - Include diagnostic information above
   - Provide specific error messages
   - Describe expected vs actual behavior
   - Include steps to reproduce

### Emergency Procedures

**If Okta account gets locked due to API errors**:

1. **Stop MCP server immediately**
   ```bash
   pkill -f mcp_okta_support
   ```

2. **Wait for lockout period** (usually 15-30 minutes)

3. **Review and fix configuration** before restarting

4. **Contact Okta support** if lockout persists

**If production system is affected**:

1. **Switch to backup authentication method**
2. **Disable automated operations**
3. **Review audit logs for root cause**
4. **Implement fix in staging environment first**