#!/usr/bin/env bash
# PropAI Skills Setup Script
# Automates environment setup, dependencies, and service initialization

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        return 1
    fi
    log_success "$1 is available"
}

# Main setup functions
setup_environment() {
    log_info "Setting up environment..."
    
    # Check required commands
    check_command "python3" || exit 1
    check_command "podman" || log_warn "Podman not found. Docker might work as alternative."
    check_command "podman-compose" || log_warn "podman-compose not found. Install with: pip install podman-compose"
    
    # Check for uv (fast Python package installer)
    if ! command -v uv &> /dev/null; then
        log_warn "uv not found. Installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    # Create .env if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env from .env.example..."
        cp .env.example .env
        log_warn "Please configure .env with your actual credentials!"
        log_warn "Required: LLM_BASE_URL, LLM_API_TOKEN, LLM_MODEL"
    else
        log_success ".env already exists"
    fi
}

install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d .venv ]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install uv in venv if not available
    if ! command -v uv &> /dev/null; then
        pip install uv
    fi
    
    # Install propai_core package
    log_info "Installing propai_core..."
    uv pip install -e packages/propai_core/
    
    # Install service dependencies
    log_info "Installing API service dependencies..."
    uv pip install -e services/api/
    
    log_info "Installing dashboard dependencies..."
    uv pip install -e services/dashboard/
    
    log_info "Installing worker dependencies..."
    uv pip install -e services/worker/
    
    # Install development dependencies
    log_info "Installing development dependencies..."
    uv pip install -e ".[dev]"
    
    log_success "All dependencies installed"
}

setup_database() {
    log_info "Setting up database..."
    
    # Start PostgreSQL and Redis containers
    log_info "Starting database containers..."
    podman-compose up -d postgres redis
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    sleep 5
    
    # Run migrations
    log_info "Running database migrations..."
    source .venv/bin/activate
    alembic upgrade head
    
    log_success "Database setup complete"
}

load_seed_data() {
    log_info "Loading seed data..."
    
    source .venv/bin/activate
    python -m seeds.run
    
    log_success "Seed data loaded"
}

start_services() {
    log_info "Starting all services..."
    
    podman-compose up -d
    
    log_success "All services started"
    log_info "Services available at:"
    log_info "  - API: http://localhost:8000"
    log_info "  - Sales Agent: http://localhost:8001"
    log_info "  - Dashboard: http://localhost:8501"
}

run_tests() {
    log_info "Running tests..."
    
    source .venv/bin/activate
    pytest tests/ -v
    
    log_success "Tests completed"
}

show_status() {
    log_info "Service status:"
    podman-compose ps
}

show_logs() {
    local service="${1:-}"
    if [ -z "$service" ]; then
        podman-compose logs -f
    else
        podman-compose logs -f "$service"
    fi
}

stop_services() {
    log_info "Stopping all services..."
    podman-compose down
    log_success "Services stopped"
}

clean_all() {
    log_warn "This will remove all containers, volumes, and virtual environment!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        podman-compose down -v
        rm -rf .venv
        log_success "Cleanup complete"
    else
        log_info "Cleanup cancelled"
    fi
}

show_help() {
    cat << EOF
PropAI Skills Setup Script

Usage: ./skills.sh [command]

Commands:
    setup       - Full setup: environment, dependencies, database, seeds
    env         - Setup environment and create .env
    deps        - Install Python dependencies
    db          - Setup database and run migrations
    seed        - Load seed data
    start       - Start all services
    stop        - Stop all services
    restart     - Restart all services
    status      - Show service status
    logs [svc]  - Show logs (optionally for specific service)
    test        - Run test suite
    clean       - Remove all containers, volumes, and venv
    help        - Show this help message

Examples:
    ./skills.sh setup          # Complete setup from scratch
    ./skills.sh start          # Start all services
    ./skills.sh logs api       # Show API service logs
    ./skills.sh test           # Run tests

Services:
    - postgres: PostgreSQL with pgvector
    - redis: Redis for job queue
    - api: FastAPI backend (port 8000)
    - sales-agent: Sales coordinator (port 8001)
    - content-agent: Content creator worker
    - dashboard: Streamlit UI (port 8501)

EOF
}

# Main command dispatcher
main() {
    local command="${1:-help}"
    
    case "$command" in
        setup)
            setup_environment
            install_dependencies
            setup_database
            load_seed_data
            start_services
            log_success "PropAI setup complete!"
            ;;
        env)
            setup_environment
            ;;
        deps)
            install_dependencies
            ;;
        db)
            setup_database
            ;;
        seed)
            load_seed_data
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "${2:-}"
            ;;
        test)
            run_tests
            ;;
        clean)
            clean_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
