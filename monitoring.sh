#!/bin/bash

# SearchNewsRAG Monitoring Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
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

# Function to start monitoring stack
start_monitoring() {
    local environment=${1:-local}

    print_status "Starting monitoring stack for $environment environment..."

    # Create monitoring network if it doesn't exist
    if ! docker network ls | grep -q "monitoring"; then
        print_status "Creating monitoring network..."
        docker network create monitoring
        print_success "Monitoring network created"
    fi

    if [ "$environment" = "prod" ]; then
        docker-compose -f docker-compose.monitoring.prod.yml up -d
    else
        docker-compose -f docker-compose.monitoring.yml up -d
    fi

    print_success "Monitoring stack started!"
    print_status "Services available at:"
    echo "  - Grafana: http://localhost:${GRAFANA_PORT:-3000} (admin/${GRAFANA_ADMIN_PASSWORD:-admin})"
    echo "  - Prometheus: http://localhost:${PROMETHEUS_PORT:-9090}"
    echo "  - Loki: http://localhost:${LOKI_PORT:-3100}"
    echo "  - Node Exporter: http://localhost:${NODE_EXPORTER_PORT:-9100}"
    echo "  - cAdvisor: http://localhost:${CADVISOR_PORT:-8080}"
}

# Function to stop monitoring stack
stop_monitoring() {
    local environment=${1:-local}

    print_status "Stopping monitoring stack for $environment environment..."

    if [ "$environment" = "prod" ]; then
        docker-compose -f docker-compose.monitoring.prod.yml down
    else
        docker-compose -f docker-compose.monitoring.yml down
    fi

    print_success "Monitoring stack stopped!"
}

# Function to restart monitoring stack
restart_monitoring() {
    local environment=${1:-local}

    print_status "Restarting monitoring stack for $environment environment..."
    stop_monitoring "$environment"
    start_monitoring "$environment"
}

# Function to view logs
logs_monitoring() {
    local service=${1:-}
    local environment=${2:-local}

    if [ -z "$service" ]; then
        print_status "Available services: grafana, prometheus, loki, promtail, node_exporter, cadvisor"
        return 1
    fi

    if [ "$environment" = "prod" ]; then
        docker-compose -f docker-compose.monitoring.prod.yml logs -f "$service"
    else
        docker-compose -f docker-compose.monitoring.yml logs -f "$service"
    fi
}

# Function to check status
status_monitoring() {
    local environment=${1:-local}

    print_status "Monitoring stack status for $environment environment:"

    if [ "$environment" = "prod" ]; then
        docker-compose -f docker-compose.monitoring.prod.yml ps
    else
        docker-compose -f docker-compose.monitoring.yml ps
    fi
}

# Function to start application with monitoring
start_full() {
    local environment=${1:-local}

    print_status "Starting full stack (application + monitoring) for $environment environment..."

    # Start monitoring first
    start_monitoring "$environment"

    # Wait a bit for monitoring to be ready
    sleep 5

    # Start application
    if [ "$environment" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml up -d
    else
        docker-compose up -d
    fi

    print_success "Full stack started!"
}

# Function to stop full stack
stop_full() {
    local environment=${1:-local}

    print_status "Stopping full stack for $environment environment..."

    # Stop application
    if [ "$environment" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml down
    else
        docker-compose down
    fi

    # Stop monitoring
    stop_monitoring "$environment"

    print_success "Full stack stopped!"
}

# Function to show help
show_help() {
    echo "SearchNewsRAG Monitoring Management Script"
    echo ""
    echo "Usage: $0 <command> [environment]"
    echo ""
    echo "Commands:"
    echo "  start [local|prod]     - Start monitoring stack"
    echo "  stop [local|prod]      - Stop monitoring stack"
    echo "  restart [local|prod]   - Restart monitoring stack"
    echo "  status [local|prod]    - Show status of monitoring stack"
    echo "  logs <service> [env]   - Show logs for a service"
    echo "  full-start [local|prod] - Start application with monitoring"
    echo "  full-stop [local|prod]  - Stop application and monitoring"
    echo "  help                   - Show this help message"
    echo ""
    echo "Services for logs: grafana, prometheus, loki, promtail, node_exporter, cadvisor"
    echo ""
    echo "Environment defaults to 'local' if not specified"
}

# Main script logic
case "$1" in
    "start")
        start_monitoring "$2"
        ;;
    "stop")
        stop_monitoring "$2"
        ;;
    "restart")
        restart_monitoring "$2"
        ;;
    "status")
        status_monitoring "$2"
        ;;
    "logs")
        logs_monitoring "$2" "$3"
        ;;
    "full-start")
        start_full "$2"
        ;;
    "full-stop")
        stop_full "$2"
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
