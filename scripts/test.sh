#!/bin/bash

# MCP Okta Support Test Script
# This script runs the test suite with various options

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
COVERAGE=false
VERBOSE=false
INTEGRATION=false
UNIT_ONLY=false
WATCH=false
PARALLEL=false
REPORT_DIR="reports"
TEST_PATTERN=""
FAIL_FAST=false

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS] [TEST_PATH]"
    echo ""
    echo "Options:"
    echo "  -c, --coverage      Run tests with coverage report"
    echo "  -v, --verbose       Run tests in verbose mode"
    echo "  -i, --integration   Run integration tests"
    echo "  -u, --unit-only     Run unit tests only"
    echo "  -w, --watch         Watch for file changes and re-run tests"
    echo "  -p, --parallel      Run tests in parallel"
    echo "  -f, --fail-fast     Stop on first failure"
    echo "  -k, --pattern       Run tests matching pattern"
    echo "  -r, --report-dir    Directory for test reports (default: reports)"
    echo "  --lint              Run linting checks"
    echo "  --type-check        Run type checking"
    echo "  --format-check      Check code formatting"
    echo "  --all-checks        Run all code quality checks"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          Run all unit tests"
    echo "  $0 -c                       Run tests with coverage"
    echo "  $0 -i                       Run integration tests"
    echo "  $0 -v -c                    Verbose tests with coverage"
    echo "  $0 -k test_user             Run tests matching 'test_user'"
    echo "  $0 tests/test_client.py     Run specific test file"
    echo "  $0 --all-checks             Run all code quality checks"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--coverage)
                COVERAGE=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -i|--integration)
                INTEGRATION=true
                shift
                ;;
            -u|--unit-only)
                UNIT_ONLY=true
                shift
                ;;
            -w|--watch)
                WATCH=true
                shift
                ;;
            -p|--parallel)
                PARALLEL=true
                shift
                ;;
            -f|--fail-fast)
                FAIL_FAST=true
                shift
                ;;
            -k|--pattern)
                TEST_PATTERN="$2"
                shift 2
                ;;
            -r|--report-dir)
                REPORT_DIR="$2"
                shift 2
                ;;
            --lint)
                LINT_ONLY=true
                shift
                ;;
            --type-check)
                TYPE_CHECK_ONLY=true
                shift
                ;;
            --format-check)
                FORMAT_CHECK_ONLY=true
                shift
                ;;
            --all-checks)
                ALL_CHECKS=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            --)
                shift
                break
                ;;
            -*)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                TEST_PATH="$1"
                shift
                ;;
        esac
    done
}

# Check if virtual environment is activated
check_venv() {
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

# Create reports directory
setup_reports() {
    if [ ! -d "$REPORT_DIR" ]; then
        mkdir -p "$REPORT_DIR"
        print_info "Created reports directory: $REPORT_DIR"
    fi
}

# Check test dependencies
check_test_dependencies() {
    print_info "Checking test dependencies..."

    # Check if pytest is installed
    if ! python -m pytest --version &> /dev/null; then
        print_error "pytest not found. Installing test dependencies..."
        pip install -e ".[dev]"
    fi

    print_success "Test dependencies available"
}

# Run linting checks
run_lint() {
    print_info "Running linting checks..."

    # Run ruff
    if command -v ruff &> /dev/null; then
        print_info "Running ruff linter..."
        ruff check src/ tests/ --output-format=text
        if [ $? -eq 0 ]; then
            print_success "Ruff linting passed"
        else
            print_error "Ruff linting failed"
            return 1
        fi
    else
        print_warning "ruff not found, skipping linting"
    fi
}

# Run type checking
run_type_check() {
    print_info "Running type checking..."

    if command -v mypy &> /dev/null; then
        print_info "Running mypy type checker..."
        mypy src/
        if [ $? -eq 0 ]; then
            print_success "Type checking passed"
        else
            print_error "Type checking failed"
            return 1
        fi
    else
        print_warning "mypy not found, skipping type checking"
    fi
}

# Run format checking
run_format_check() {
    print_info "Checking code formatting..."

    if command -v black &> /dev/null; then
        print_info "Running black format checker..."
        black --check src/ tests/
        if [ $? -eq 0 ]; then
            print_success "Code formatting is correct"
        else
            print_error "Code formatting issues found"
            print_info "Run 'black src/ tests/' to fix formatting"
            return 1
        fi
    else
        print_warning "black not found, skipping format checking"
    fi
}

# Run all code quality checks
run_all_checks() {
    print_info "Running all code quality checks..."

    local failed=0

    run_lint || failed=$((failed + 1))
    run_type_check || failed=$((failed + 1))
    run_format_check || failed=$((failed + 1))

    if [ $failed -eq 0 ]; then
        print_success "All code quality checks passed"
        return 0
    else
        print_error "$failed code quality check(s) failed"
        return 1
    fi
}

# Build pytest command
build_pytest_cmd() {
    local cmd="python -m pytest"

    # Add test path
    if [ ! -z "$TEST_PATH" ]; then
        cmd="$cmd $TEST_PATH"
    elif [ "$UNIT_ONLY" = true ]; then
        cmd="$cmd tests/ -k 'not integration'"
    elif [ "$INTEGRATION" = true ]; then
        cmd="$cmd tests/integration/"
    else
        cmd="$cmd tests/"
    fi

    # Add options
    if [ "$VERBOSE" = true ]; then
        cmd="$cmd -v"
    fi

    if [ "$FAIL_FAST" = true ]; then
        cmd="$cmd -x"
    fi

    if [ "$PARALLEL" = true ]; then
        cmd="$cmd -n auto"
    fi

    if [ ! -z "$TEST_PATTERN" ]; then
        cmd="$cmd -k '$TEST_PATTERN'"
    fi

    # Add coverage options
    if [ "$COVERAGE" = true ]; then
        cmd="$cmd --cov=mcp_okta_support"
        cmd="$cmd --cov-report=html:$REPORT_DIR/coverage"
        cmd="$cmd --cov-report=xml:$REPORT_DIR/coverage.xml"
        cmd="$cmd --cov-report=term-missing"
    fi

    # Add junit XML report
    cmd="$cmd --junit-xml=$REPORT_DIR/junit.xml"

    echo "$cmd"
}

# Run tests
run_tests() {
    print_info "Running tests..."

    local pytest_cmd=$(build_pytest_cmd)
    print_info "Command: $pytest_cmd"

    # Set test environment variables
    export TESTING=true
    export MCP_LOG_LEVEL=ERROR  # Reduce log noise during tests

    # Run the tests
    eval $pytest_cmd

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_success "All tests passed"
    else
        print_error "Some tests failed (exit code: $exit_code)"
    fi

    return $exit_code
}

# Watch mode
run_watch() {
    print_info "Starting watch mode..."
    print_info "Watching for changes in src/ and tests/ directories"
    print_info "Press Ctrl+C to stop"

    if command -v pytest-watch &> /dev/null; then
        pytest-watch --runner "$(build_pytest_cmd)"
    elif command -v watchdog &> /dev/null; then
        watchdog "$(build_pytest_cmd)" src/ tests/
    else
        print_error "Watch mode requires pytest-watch or watchdog"
        print_info "Install with: pip install pytest-watch"
        exit 1
    fi
}

# Generate test report
generate_report() {
    if [ "$COVERAGE" = true ] && [ -f "$REPORT_DIR/coverage.xml" ]; then
        print_info "Coverage report generated:"
        print_info "  - HTML: $REPORT_DIR/coverage/index.html"
        print_info "  - XML: $REPORT_DIR/coverage.xml"
    fi

    if [ -f "$REPORT_DIR/junit.xml" ]; then
        print_info "JUnit XML report: $REPORT_DIR/junit.xml"
    fi
}

# Show test summary
show_summary() {
    echo ""
    print_info "============================================"
    print_info "Test Summary"
    print_info "============================================"

    if [ "$COVERAGE" = true ]; then
        # Show coverage summary if available
        if command -v coverage &> /dev/null && [ -f ".coverage" ]; then
            coverage report --show-missing
        fi
    fi

    generate_report
}

# Main function
main() {
    parse_args "$@"

    echo ""
    print_info "============================================"
    print_info "MCP Okta Support Test Runner"
    print_info "============================================"
    echo ""

    check_venv
    setup_reports
    check_test_dependencies

    # Handle special modes
    if [ "$LINT_ONLY" = true ]; then
        run_lint
        exit $?
    fi

    if [ "$TYPE_CHECK_ONLY" = true ]; then
        run_type_check
        exit $?
    fi

    if [ "$FORMAT_CHECK_ONLY" = true ]; then
        run_format_check
        exit $?
    fi

    if [ "$ALL_CHECKS" = true ]; then
        run_all_checks
        exit $?
    fi

    # Watch mode
    if [ "$WATCH" = true ]; then
        run_watch
        exit $?
    fi

    # Normal test run
    local exit_code=0

    # Run code quality checks first (if not explicitly disabled)
    if [ "$SKIP_CHECKS" != true ]; then
        print_info "Running code quality checks..."
        run_all_checks || print_warning "Code quality checks failed (continuing with tests)"
        echo ""
    fi

    # Run tests
    run_tests || exit_code=$?

    # Show summary
    show_summary

    exit $exit_code
}

# Run main function
main "$@"