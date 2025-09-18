#!/bin/bash

# MCP Okta Support Start Script
# This script starts the MCP server with proper environment setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
DEVELOPMENT_MODE=false
LOG_LEVEL="INFO"
CONFIG_FILE=".env"
PORT=""
VERBOSE=false

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --dev          Run in development mode"
    echo "  -v, --verbose      Enable verbose logging (DEBUG level)"
    echo "  -l, --log-level    Set log level (DEBUG, INFO, WARNING, ERROR)"
    echo "  -c, --config       Specify config file (default: .env)"
    echo "  -p, --port         Specify port number"
    echo "  --check            Check configuration and exit"
    echo "  --test-connection  Test Okta connection and exit"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 Start server with default settings"
    echo "  $0 -d              Start in development mode"
    echo "  $0 -v              Start with verbose logging"
    echo "  $0 --check         Check configuration only"
    echo "  $0 --test-connection  Test Okta API connection"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dev)
                DEVELOPMENT_MODE=true
                LOG_LEVEL="DEBUG"
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                LOG_LEVEL="DEBUG"
                shift
                ;;
            -l|--log-level)
                LOG_LEVEL="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            --check)
                CHECK_ONLY=true
                shift
                ;;
            --test-connection)
                TEST_CONNECTION=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Check if virtual environment exists and is activated
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Run setup.sh first."
        exit 1
    fi

    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_info "Activating virtual environment..."
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
        print_success "Virtual environment activated"
    fi
}

# Check configuration file
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file $CONFIG_FILE not found"
        print_info "Run setup.sh to create configuration file"
        exit 1
    fi

    print_success "Configuration file found: $CONFIG_FILE"
}

# Load environment variables
load_environment() {
    print_info "Loading environment variables from $CONFIG_FILE"

    # Export variables from config file
    set -a
    source "$CONFIG_FILE"
    set +a

    # Override with command line options
    if [ "$DEVELOPMENT_MODE" = true ]; then
        export DEVELOPMENT_MODE=true
    fi

    if [ ! -z "$LOG_LEVEL" ]; then
        export MCP_LOG_LEVEL="$LOG_LEVEL"
    fi

    if [ ! -z "$PORT" ]; then
        export MCP_PORT="$PORT"
    fi

    print_success "Environment variables loaded"
}

# Validate configuration
validate_config() {
    print_info "Validating configuration..."

    # Check required variables
    if [ -z "$OKTA_ORG_URL" ]; then
        print_error "OKTA_ORG_URL is not set"
        exit 1
    fi

    # Check authentication method
    if [ -z "$OKTA_API_TOKEN" ] && [ -z "$OKTA_CLIENT_ID" ]; then
        print_error "Either OKTA_API_TOKEN or OKTA_CLIENT_ID must be set"
        exit 1
    fi

    # Validate URL format
    if [[ ! "$OKTA_ORG_URL" =~ ^https://.*\.okta\.com$ ]] && [[ ! "$OKTA_ORG_URL" =~ ^https://.*\.oktapreview\.com$ ]]; then
        print_warning "OKTA_ORG_URL format looks unusual: $OKTA_ORG_URL"
    fi

    print_success "Configuration validation passed"
}

# Test Okta connection
test_okta_connection() {
    print_info "Testing Okta API connection..."

    if [ ! -z "$OKTA_API_TOKEN" ]; then
        # Test with API token
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: SSWS $OKTA_API_TOKEN" \
            -H "Accept: application/json" \
            "$OKTA_ORG_URL/api/v1/users/me")

        if [ "$response" = "200" ]; then
            print_success "Okta API connection successful (API Token)"
        else
            print_error "Okta API connection failed (HTTP $response)"
            print_info "Check your OKTA_API_TOKEN and OKTA_ORG_URL"
            exit 1
        fi
    elif [ ! -z "$OKTA_CLIENT_ID" ]; then
        # Test OAuth token exchange
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "grant_type=client_credentials&scope=okta.users.read" \
            -u "$OKTA_CLIENT_ID:$OKTA_CLIENT_SECRET" \
            "$OKTA_ORG_URL/oauth2/default/v1/token")

        if [ "$response" = "200" ]; then
            print_success "Okta OAuth connection successful"
        else
            print_error "Okta OAuth connection failed (HTTP $response)"
            print_info "Check your OKTA_CLIENT_ID, OKTA_CLIENT_SECRET, and OKTA_ORG_URL"
            exit 1
        fi
    fi
}

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."

    python -c "import mcp_okta_support" 2>/dev/null
    if [ $? -ne 0 ]; then
        print_error "mcp_okta_support package not found"
        print_info "Run: pip install -e ."
        exit 1
    fi

    print_success "Dependencies check passed"
}

# Start the server
start_server() {
    print_info "Starting MCP Okta Support server..."
    print_info "Configuration:"
    print_info "  - Okta Org: $OKTA_ORG_URL"
    print_info "  - Auth Method: $([ ! -z "$OKTA_API_TOKEN" ] && echo "API Token" || echo "OAuth 2.0")"
    print_info "  - Log Level: $MCP_LOG_LEVEL"
    print_info "  - Development Mode: $DEVELOPMENT_MODE"

    if [ "$VERBOSE" = true ]; then
        print_info "  - Port: ${MCP_PORT:-"default"}"
        print_info "  - Rate Limit: ${OKTA_RATE_LIMIT:-"100"}"
        print_info "  - Timeout: ${OKTA_TIMEOUT_SECONDS:-"30"}s"
    fi

    echo ""
    print_info "Starting server... (Press Ctrl+C to stop)"
    echo ""

    # Start the server
    python -m mcp_okta_support.main
}

# Handle configuration check only
handle_check_only() {
    print_info "Configuration check mode"
    validate_config
    print_success "Configuration is valid"
    exit 0
}

# Handle connection test only
handle_test_connection() {
    print_info "Connection test mode"
    validate_config
    test_okta_connection
    print_success "Connection test passed"
    exit 0
}

# Show server info
show_server_info() {
    echo ""
    print_info "============================================"
    print_info "MCP Okta Support Server"
    print_info "============================================"
    echo ""
}

# Cleanup function
cleanup() {
    echo ""
    print_info "Shutting down server..."
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Main function
main() {
    parse_args "$@"
    show_server_info

    # Handle special modes
    if [ "$CHECK_ONLY" = true ]; then
        handle_check_only
    fi

    if [ "$TEST_CONNECTION" = true ]; then
        handle_test_connection
    fi

    # Normal startup
    check_venv
    check_config
    load_environment
    validate_config
    check_dependencies

    # Test connection unless skipped
    if [ "$SKIP_CONNECTION_TEST" != true ]; then
        test_okta_connection
    fi

    # Start server
    start_server
}

# Run main function
main "$@"