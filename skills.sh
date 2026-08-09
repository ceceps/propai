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

get_sudo_prefix() {
    if [ "$(id -u)" -eq 0 ]; then
        echo ""
    elif command -v sudo >/dev/null 2>&1; then
        echo "sudo"
    else
        echo ""
    fi
}

get_compose_command() {
    local sudo_prefix
    sudo_prefix="$(get_sudo_prefix)"

    if [ -S /var/run/docker.sock ] && ! docker info >/dev/null 2>&1; then
        if [ -n "$sudo_prefix" ]; then
            echo "$sudo_prefix docker"
            return 0
        fi
    fi

    echo "docker"
}

check_runtime_requirements() {
    local missing=0

    for tool in python3 curl; do
        if command -v "$tool" >/dev/null 2>&1; then
            log_success "$tool is available"
        else
            log_warn "$tool is missing"
            missing=1
        fi
    done

    if [ -d .venv ]; then
        log_success ".venv exists"
    else
        log_warn ".venv is missing; run deps first"
        missing=1
    fi

    if command -v redis-server >/dev/null 2>&1; then
        log_success "redis-server is available"
    else
        log_warn "redis-server is missing"
        missing=1
    fi

    if command -v psql >/dev/null 2>&1; then
        log_success "psql is available"
    else
        log_warn "psql is missing"
        missing=1
    fi

    if command -v initdb >/dev/null 2>&1 && command -v pg_ctl >/dev/null 2>&1; then
        log_success "postgres binaries are available"
    else
        log_warn "postgres binaries are missing"
        missing=1
    fi

    if [ "$missing" -eq 0 ]; then
        log_success "Core local runtime requirements look good"
    else
        log_warn "Some runtime requirements are missing; install them before a full local run"
    fi
}

port_in_use() {
    local port="$1"
    python3 - <<'PY' "$port"
import socket
import sys

port = int(sys.argv[1])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(1)
    try:
        sock.connect(("127.0.0.1", port))
    except OSError:
        sys.exit(1)
    sys.exit(0)
PY
}

ensure_local_redis() {
    if redis-cli ping >/dev/null 2>&1; then
        log_success "Redis is already running"
        return 0
    fi

    if ! command -v redis-server >/dev/null 2>&1; then
        log_warn "redis-server not found; skipping Redis startup"
        return 1
    fi

    local redis_dir="${REDIS_DATA_DIR:-/tmp/redis-data}"
    mkdir -p "$redis_dir"
    redis-server --daemonize yes --dir "$redis_dir" --port 6379

    if redis-cli ping >/dev/null 2>&1; then
        log_success "Redis started locally"
        return 0
    fi

    log_warn "Redis could not be started"
    return 1
}

ensure_local_postgres() {
    if pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
        log_success "PostgreSQL is already running"
        return 0
    fi

    if ! command -v initdb >/dev/null 2>&1 || ! command -v pg_ctl >/dev/null 2>&1; then
        log_warn "PostgreSQL binaries not found; skipping PostgreSQL startup"
        return 1
    fi

    local sudo_prefix
    sudo_prefix="$(get_sudo_prefix)"
    local pgdata_dir="${PGDATA_DIR:-/tmp/pgdata}"
    local pglog_dir="${PGLOG_DIR:-/var/tmp/pglogs}"

    mkdir -p "$pgdata_dir" "$pglog_dir"
    if [ -n "$sudo_prefix" ]; then
        $sudo_prefix mkdir -p "$pgdata_dir" "$pglog_dir"
        $sudo_prefix chown -R postgres:postgres "$pgdata_dir" "$pglog_dir"
        $sudo_prefix -u postgres initdb -D "$pgdata_dir" >"$pglog_dir/initdb.log" 2>&1
        $sudo_prefix -u postgres pg_ctl -D "$pgdata_dir" -l "$pglog_dir/postgres.log" -o "-k /tmp -p 5432" start
    else
        initdb -D "$pgdata_dir" >"$pglog_dir/initdb.log" 2>&1
        pg_ctl -D "$pgdata_dir" -l "$pglog_dir/postgres.log" -o "-k /tmp -p 5432" start
    fi

    sleep 2
    if pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
        log_success "PostgreSQL started locally"
        return 0
    fi

    log_warn "PostgreSQL could not be started"
    return 1
}

ensure_local_services() {
    ensure_local_redis || true
    ensure_local_postgres || true
}

ensure_compose_runtime() {
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
        COMPOSE_RUNTIME="docker"
        log_success "Using Docker Compose"
        return 0
    fi

    if command -v podman >/dev/null 2>&1; then
        COMPOSE_RUNTIME="podman"
        log_success "Using Podman Compose"
        return 0
    fi

    log_warn "No Docker or Podman runtime detected. Attempting to install one..."

    local sudo_prefix
    sudo_prefix="$(get_sudo_prefix)"

    if [ -f /etc/alpine-release ]; then
        log_info "Installing Podman and podman-compose on Alpine"
        if ! $sudo_prefix apk update; then
            log_error "Failed to update Alpine package indexes"
            return 1
        fi
        if ! $sudo_prefix apk add --no-cache podman podman-compose; then
            log_error "Failed to install Podman and podman-compose"
            return 1
        fi
        COMPOSE_RUNTIME="podman"
        return 0
    fi

    if command -v apt-get >/dev/null 2>&1; then
        log_info "Installing Docker Compose support on Debian/Ubuntu"
        if ! $sudo_prefix apt-get update; then
            log_error "Failed to update apt package indexes"
            return 1
        fi
        if ! $sudo_prefix apt-get install -y docker.io docker-compose-plugin; then
            log_error "Failed to install Docker Compose support"
            return 1
        fi
        COMPOSE_RUNTIME="docker"
        return 0
    fi

    log_error "Could not install a supported container runtime automatically"
    return 1
}

run_compose() {
    if [ -z "${COMPOSE_RUNTIME:-}" ]; then
        ensure_compose_runtime || return 1
    fi

    case "$COMPOSE_RUNTIME" in
        docker)
            local docker_cmd
            docker_cmd="$(get_compose_command)"
            if [ "$docker_cmd" = "docker" ]; then
                docker compose "$@"
            else
                $docker_cmd compose "$@"
            fi
            ;;
        podman)
            if command -v podman-compose >/dev/null 2>&1; then
                podman-compose "$@"
            else
                podman compose "$@"
            fi
            ;;
        *)
            log_error "Unsupported compose runtime: $COMPOSE_RUNTIME"
            return 1
            ;;
    esac
}

# Main setup functions
setup_environment() {
    log_info "Setting up environment..."
    
    # Check required commands
    check_command "python3" || exit 1
    check_runtime_requirements
    ensure_compose_runtime || true
    
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
    export UV_LINK_MODE=copy
    uv pip install pytest pytest-asyncio ruff mypy
    
    log_success "All dependencies installed"
}

setup_database() {
    log_info "Setting up database..."

    if run_compose up -d postgres redis >/dev/null 2>&1; then
        log_info "Waiting for PostgreSQL to be ready..."
        sleep 5

        log_info "Running database migrations..."
        source .venv/bin/activate
        if alembic upgrade head; then
            DB_READY=1
            log_success "Database setup complete"
        else
            DB_READY=0
            log_warn "Database migrations failed; database is not ready."
        fi
    else
        log_warn "Container runtime is unavailable; falling back to local PostgreSQL and Redis."
        ensure_local_services

        source .venv/bin/activate
        if alembic upgrade head; then
            DB_READY=1
            log_success "Database setup complete"
        else
            DB_READY=0
            log_warn "Database migrations failed; database is not ready."
        fi
    fi
}

load_seed_data() {
    if [ "${DB_READY:-0}" != "1" ]; then
        log_warn "Skipping seed data because the database is not available."
        return 0
    fi

    log_info "Loading seed data..."

    source .venv/bin/activate
    if python -m seeds.run; then
        log_success "Seed data loaded"
    else
        log_warn "Seed data load failed; the database may still be unavailable."
    fi
}

start_services() {
    log_info "Starting all services..."

    if [ -d .venv ]; then
        source .venv/bin/activate
    fi

    if run_compose up -d >/dev/null 2>&1; then
        log_success "All services started via compose"
        log_info "Services available at:"
        log_info "  - API: http://localhost:8000"
        log_info "  - Sales Agent: http://localhost:8001"
        log_info "  - Dashboard: http://localhost:8501"
        return 0
    fi

    log_warn "Container runtime is unavailable; starting services locally instead."
    ensure_local_services

    local log_dir="${LOG_DIR:-/tmp/propai-logs}"
    mkdir -p "$log_dir"

    export PYTHONPATH="/workspaces/propai/packages/propai_core/src:/workspaces/propai/services/api/src:/workspaces/propai/services/dashboard/src"

    if ! port_in_use 8000; then
        nohup uvicorn propai_api.main:app --host 127.0.0.1 --port 8000 >"$log_dir/api.log" 2>&1 &
        log_info "API started in background"
    else
        log_success "API is already running on http://localhost:8000"
    fi

    if ! port_in_use 8501; then
        nohup streamlit run services/dashboard/src/propai_dashboard/app.py --server.address 127.0.0.1 --server.port 8501 >"$log_dir/dashboard.log" 2>&1 &
        log_info "Dashboard started in background"
    else
        log_success "Dashboard is already running on http://localhost:8501"
    fi

    sleep 3
    log_success "Local services started"
    log_info "Services available at:"
    log_info "  - API: http://localhost:8000"
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
    run_compose ps
}

show_logs() {
    local service="${1:-}"
    if [ -z "$service" ]; then
        run_compose logs -f
    else
        run_compose logs -f "$service"
    fi
}

stop_services() {
    log_info "Stopping all services..."
    run_compose down
    log_success "Services stopped"
}

clean_all() {
    log_warn "This will remove all containers, volumes, and virtual environment!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        run_compose down -v
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
