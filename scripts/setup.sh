#!/bin/bash

# MCP Okta Support Setup Script
# This script sets up the MCP Okta Support project

set -e  # Exit on any error

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

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    print_info "Detected OS: $OS"
}

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.9 or higher."
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d" " -f2)
    REQUIRED_VERSION="3.9.0"

    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
        print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python $PYTHON_VERSION found"
}

# Check pip
check_pip() {
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_error "pip is not installed. Please install pip."
        exit 1
    fi

    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi

    print_success "pip found"
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."

    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
        return
    fi

    $PYTHON_CMD -m venv venv

    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."

    if [[ "$OS" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi

    if [ $? -eq 0 ]; then
        print_success "Virtual environment activated"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."

    # Upgrade pip first
    pip install --upgrade pip

    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found"
        exit 1
    fi

    # Install package in development mode
    pip install -e .

    print_success "Dependencies installed"
}

# Setup environment file
setup_environment() {
    print_info "Setting up environment configuration..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
            print_warning "Please edit .env file with your Okta configuration"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_warning ".env file already exists. Skipping creation."
    fi
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."

    # Test import
    python -c "import mcp_okta_support; print('✓ Package imports successfully')" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Package import test passed"
    else
        print_error "Package import test failed"
        exit 1
    fi

    # Test configuration loading (without Okta credentials)
    python -c "
from mcp_okta_support.config import Settings
import os
os.environ['OKTA_ORG_URL'] = 'https://test.okta.com'
os.environ['OKTA_API_TOKEN'] = 'test_token'
try:
    s = Settings()
    print('✓ Configuration loading works')
except Exception as e:
    print(f'✗ Configuration loading failed: {e}')
    exit(1)
" 2>/dev/null

    if [ $? -eq 0 ]; then
        print_success "Configuration test passed"
    else
        print_error "Configuration test failed"
        exit 1
    fi

    print_success "Installation verification completed"
}

# Show next steps
show_next_steps() {
    echo ""
    print_info "============================================"
    print_info "Setup completed successfully!"
    print_info "============================================"
    echo ""
    print_info "Next steps:"
    echo "1. Edit the .env file with your Okta configuration:"
    echo "   nano .env"
    echo ""
    echo "2. Required environment variables:"
    echo "   - OKTA_ORG_URL: Your Okta organization URL"
    echo "   - OKTA_API_TOKEN: Your Okta API token (OR OAuth credentials)"
    echo ""
    echo "3. Test your configuration:"
    if [[ "$OS" == "windows" ]]; then
        echo "   venv\\Scripts\\activate"
    else
        echo "   source venv/bin/activate"
    fi
    echo "   python -m mcp_okta_support.main"
    echo ""
    echo "4. Read the documentation:"
    echo "   - docs/setup.md - Detailed setup instructions"
    echo "   - docs/usage.md - Usage examples"
    echo "   - docs/troubleshooting.md - Common issues"
    echo ""
    print_info "For support, see: https://github.com/your-org/mcp-okta-support"
}

# Main function
main() {
    echo ""
    print_info "============================================"
    print_info "MCP Okta Support Setup Script"
    print_info "============================================"
    echo ""

    # Check prerequisites
    check_os
    check_python
    check_pip

    # Setup project
    create_venv
    activate_venv
    install_dependencies
    setup_environment

    # Verify installation
    verify_installation

    # Show next steps
    show_next_steps
}

# Run main function
main "$@"