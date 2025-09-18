# Architecture Overview

## System Architecture

MCP Okta Support follows the Model Context Protocol (MCP) pattern, enabling seamless integration between local LLMs and Okta APIs.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           User                                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Natural Language Commands
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Local LLM Host                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              MCP Client (Embedded)                          │ │
│  │  • Protocol management                                      │ │
│  │  • Tool discovery                                           │ │
│  │  • Request/response handling                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────────┘
                       │ MCP Protocol (JSON-RPC)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server (This Project)                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   FastMCP       │  │   Tool Registry │  │   Resources     │  │
│  │   Server        │  │   • Users       │  │   • Templates   │  │
│  │                 │  │   • Apps        │  │   • Examples    │  │
│  │                 │  │   • Logs        │  │   • Help        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Config        │  │   Okta Client   │  │   Error         │  │
│  │   Management    │  │   • Auth        │  │   Handling      │  │
│  │                 │  │   • Rate Limit  │  │                 │  │
│  │                 │  │   • Retry       │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS API Calls
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Okta APIs                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Users API     │  │   Apps API      │  │   System Logs   │  │
│  │   /api/v1/users │  │   /api/v1/apps  │  │   /api/v1/logs  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Local LLM Host

**Purpose**: User interface and natural language processing
**Examples**: Ollama, gpt-oss, Claude Desktop
**Responsibilities**:
- Parse user natural language commands
- Communicate with MCP server via protocol
- Present responses to user

### 2. MCP Client (Embedded)

**Purpose**: Protocol management within the LLM host
**Responsibilities**:
- Implement MCP protocol specification
- Discover available tools and resources
- Handle request/response serialization
- Manage connection lifecycle

### 3. MCP Server (This Project)

**Purpose**: Bridge between MCP protocol and Okta APIs
**Key Components**:

#### FastMCP Server
- **File**: `src/mcp_okta_support/mcp/server.py`
- **Purpose**: MCP protocol implementation
- **Features**: Tool registration, resource exposure, server info

#### Tool Registry
- **File**: `src/mcp_okta_support/mcp/tools.py`
- **Purpose**: Define available MCP tools
- **Tools**: User management, app management, log search

#### Resource Registry
- **File**: `src/mcp_okta_support/mcp/resources.py`
- **Purpose**: Expose static resources
- **Resources**: Templates, examples, help documentation

#### Configuration Management
- **File**: `src/mcp_okta_support/config.py`
- **Purpose**: Environment-based configuration
- **Features**: Validation, OAuth/API token support

#### Okta Client
- **File**: `src/mcp_okta_support/okta/client.py`
- **Purpose**: HTTP client for Okta APIs
- **Features**: Authentication, rate limiting, error handling

### 4. Okta APIs

**Purpose**: Backend services for user and application management
**Key APIs**:
- **Users API**: User CRUD operations, lifecycle management
- **Applications API**: App configuration and assignments
- **System Logs API**: Audit logs and event search

## Data Flow

### 1. Command Processing

```
User Input: "Get details for user john.doe@company.com"
     ↓
LLM Host: Parse intent → identify get_user_details tool
     ↓
MCP Client: Send tool execution request
     ↓
MCP Server: Receive request → validate parameters
     ↓
Okta Client: GET /api/v1/users/john.doe@company.com
     ↓
Okta API: Return user data
     ↓
MCP Server: Format response → return to client
     ↓
MCP Client: Receive response → pass to LLM
     ↓
LLM Host: Generate natural language response
     ↓
User: Receive formatted user information
```

### 2. Error Handling Flow

```
API Error Occurs
     ↓
Okta Client: Detect error type (4xx, 5xx, timeout)
     ↓
Exception Handler: Create appropriate exception
     ↓
Tool Layer: Catch exception → format error response
     ↓
MCP Server: Return error response with details
     ↓
LLM Host: Present user-friendly error message
```

## Security Architecture

### Authentication Flow

#### API Token Flow
```
MCP Server Startup
     ↓
Load OKTA_API_TOKEN from environment
     ↓
Add "Authorization: SSWS {token}" header
     ↓
All API requests include authentication
```

#### OAuth 2.0 Flow
```
MCP Server Startup
     ↓
Load OKTA_CLIENT_ID and OKTA_CLIENT_SECRET
     ↓
Request access token via client credentials
     ↓
Add "Authorization: Bearer {token}" header
     ↓
Refresh token when needed
```

### Security Layers

1. **Environment Isolation**: Credentials stored in environment variables
2. **Input Validation**: All user inputs validated before API calls
3. **Rate Limiting**: Prevent API abuse with configurable limits
4. **Error Sanitization**: Sensitive data removed from error messages
5. **Audit Logging**: All operations logged for security review

## Performance Considerations

### Rate Limiting Strategy

```python
class RateLimiter:
    - Track requests per minute
    - Honor Okta rate limit headers
    - Automatic backoff on rate limit exceeded
    - Configurable limits per deployment
```

### Caching Strategy

- **No caching**: All data retrieved fresh for accuracy
- **Connection pooling**: HTTP client reuses connections
- **Async operations**: Non-blocking I/O for better performance

### Error Recovery

```
Network Error
     ↓
Automatic Retry (configurable attempts)
     ↓
Exponential Backoff
     ↓
Circuit Breaker (if multiple failures)
     ↓
Graceful Degradation
```

## Extensibility

### Adding New Tools

1. **Define Tool Function**:
   ```python
   @mcp.tool()
   async def new_operation(param: str) -> Dict[str, Any]:
       # Implementation
   ```

2. **Add to Tool Registry**: Register in `tools.py`

3. **Add Client Method**: Implement in appropriate manager class

4. **Add Tests**: Unit and integration tests

### Adding New Resources

1. **Define Resource**:
   ```python
   @mcp.resource("okta://templates/new_template")
   def get_new_template() -> Dict[str, Any]:
       # Return template data
   ```

2. **Register**: Add to `resources.py`

### Configuration Extensions

1. **Add Setting**: Extend `Settings` class in `config.py`
2. **Add Validation**: Include validators if needed
3. **Update Documentation**: Update `.env.example`

## Deployment Patterns

### Local Development
```
Developer Machine
├── Python Environment
├── Environment Variables (.env)
├── MCP Server Process
└── Local LLM Connection
```

### Docker Deployment
```
Container Environment
├── Python Runtime
├── Environment Variables (docker-compose.yml)
├── MCP Server Process
└── Network Access to LLM Host
```

### Production Deployment
```
Server Environment
├── Secrets Management (Vault, K8s Secrets)
├── Container Orchestration
├── Load Balancing (if multiple instances)
├── Monitoring and Logging
└── Security Scanning
```

## Monitoring and Observability

### Logging Architecture

```
Application Events
     ↓
Structured Logging (structlog)
     ↓
Log Levels: DEBUG, INFO, WARNING, ERROR
     ↓
Output Formats: JSON (production), Pretty (development)
     ↓
Log Aggregation (Optional: ELK, Splunk)
```

### Metrics

- **Request Count**: Number of API calls made
- **Response Times**: Latency for API operations
- **Error Rates**: Failed requests by type
- **Rate Limit Usage**: Current usage vs limits

### Health Checks

- **Server Health**: `/server://health` resource
- **Okta Connectivity**: API connection test
- **Authentication**: Token validity check