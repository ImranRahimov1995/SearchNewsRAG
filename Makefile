.PHONY: help install test lint format check coverage clean pre-commit

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	poetry install --with dev
	poetry run pre-commit install
	poetry run pre-commit install --hook-type pre-push

test: ## Run all tests
	poetry run pytest -v

test-cov: ## Run tests with coverage
	poetry run pytest --cov --cov-report=html --cov-report=term

test-fast: ## Run tests with minimal output
	poetry run pytest --tb=short --maxfail=3

lint: ## Run all linters
	poetry run ruff check .
	poetry run mypy --config-file pyproject.toml telegram_fetcher/ rag_module/ backend/
	poetry run bandit -c pyproject.toml -r telegram_fetcher/ rag_module/ backend/

format: ## Format code with black and isort
	poetry run black .
	poetry run isort .
	poetry run ruff check . --fix

check: ## Run all checks (format + lint + test)
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test

ci: ## Run CI checks (matches GitHub Actions)
	poetry run pre-commit run --all-files
	poetry run pytest --cov --cov-report=xml --cov-report=term

pre-commit: ## Run pre-commit on all files
	poetry run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	poetry run pre-commit autoupdate

coverage: ## Open coverage report in browser
	poetry run pytest --cov --cov-report=html
	@echo "Opening coverage report..."
	@xdg-open htmlcov/index.html 2>/dev/null || \
		open htmlcov/index.html 2>/dev/null || \
		echo "Open htmlcov/index.html manually"

clean: ## Clean cache and temp files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

clean-all: clean ## Clean everything including virtualenv
	poetry env remove --all

setup: ## First-time setup
	@echo "🚀 Setting up development environment..."
	poetry install --with dev
	poetry run pre-commit install
	poetry run pre-commit install --hook-type pre-push
	@echo "✅ Setup complete! Run 'make test' to verify."

# Development workflow shortcuts
dev-check: format lint test-fast ## Quick development check

# Database migrations
migrate-up: ## Run database migrations to latest version
	cd backend && poetry run python -m src.migrations upgrade

migrate-down: ## Rollback last migration
	cd backend && poetry run python -m src.migrations downgrade

migrate-current: ## Show current migration revision
	cd backend && poetry run python -m src.migrations current

migrate-pending: ## Check if migrations are pending
	cd backend && poetry run python -m src.migrations pending

migrate-create: ## Create new migration (use: make migrate-create name="your_migration_name")
	cd backend && poetry run alembic revision --autogenerate -m "$(name)"

# Monitoring commands
monitoring-start: ## Start monitoring stack (local)
	./monitoring.sh start local

monitoring-start-prod: ## Start monitoring stack (production)
	./monitoring.sh start prod

monitoring-stop: ## Stop monitoring stack (local)
	./monitoring.sh stop local

monitoring-stop-prod: ## Stop monitoring stack (production)
	./monitoring.sh stop prod

monitoring-restart: ## Restart monitoring stack (local)
	./monitoring.sh restart local

monitoring-restart-prod: ## Restart monitoring stack (production)
	./monitoring.sh restart prod

monitoring-status: ## Show monitoring stack status (local)
	./monitoring.sh status local

monitoring-status-prod: ## Show monitoring stack status (production)
	./monitoring.sh status prod

monitoring-logs: ## Show Grafana logs (use: make monitoring-logs service=grafana)
	./monitoring.sh logs $(service) local

monitoring-logs-prod: ## Show monitoring service logs (use: make monitoring-logs-prod service=grafana)
	./monitoring.sh logs $(service) prod

full-start: ## Start application with monitoring (local)
	./monitoring.sh full-start local

full-start-prod: ## Start application with monitoring (production)
	./monitoring.sh full-start prod

full-stop: ## Stop application and monitoring (local)
	./monitoring.sh full-stop local

full-stop-prod: ## Stop application and monitoring (production)
	./monitoring.sh full-stop prod

# Docker commands
docker-build: ## Build all Docker images
	docker-compose build

docker-build-prod: ## Build production Docker images
	docker-compose -f docker-compose.prod.yml build

docker-up: ## Start application containers
	docker-compose up -d

docker-up-prod: ## Start production containers
	docker-compose -f docker-compose.prod.yml up -d

docker-down: ## Stop application containers
	docker-compose down

docker-down-prod: ## Stop production containers
	docker-compose -f docker-compose.prod.yml down

docker-logs: ## Show application logs
	docker-compose logs -f

docker-logs-prod: ## Show production logs
	docker-compose -f docker-compose.prod.yml logs -f
