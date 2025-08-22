# Makefile for Apache Airflow Project (Docker-based)

# Variables
DOCKER_IMAGE = airflow-dev
DOCKER_CONTAINER = airflow_dev
COMPOSE_FILE = docker-compose.yml

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  Docker:"
	@echo "    build          - Build the Docker image"
	@echo "    up             - Start Airflow in standalone mode (detached)"
	@echo "    down           - Stop and remove containers"
	@echo "    logs           - Show container logs"
	@echo "    shell          - Open a shell in the running container"
	@echo "    restart        - Restart the Airflow container"
	@echo ""
	@echo "  Development:"
	@echo "    test           - Run all tests in container"
	@echo "    test-watch     - Run tests in watch mode"
	@echo "    lint           - Run linting checks in container"
	@echo "    format         - Format code with black and isort"
	@echo "    clean          - Clean up Docker resources and cache files"
	@echo ""
	@echo "  Airflow:"
	@echo "    airflow-init   - Initialize Airflow database in container"
	@echo "    airflow-start  - Start Airflow (alias for 'up')"
	@echo "    airflow-stop   - Stop Airflow (alias for 'down')"
	@echo "    airflow-test   - Test DAG syntax and imports"
	@echo "    airflow-list   - List all DAGs"
	@echo "    airflow-web    - Access Airflow webserver (http://localhost:8080)"
	@echo ""
	@echo "  Database:"
	@echo "    db-migrate     - Run database migrations"
	@echo "    db-reset       - Reset Airflow database"
	@echo ""
	@echo "  Utilities:"
	@echo "    status         - Show container status"
	@echo "    check-deps     - Check for dependency issues"

# Docker Commands
.PHONY: build
build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .
	@echo "Docker image built successfully!"

.PHONY: up
up:
	@echo "Starting Airflow in standalone mode..."
	@echo "Webserver will be available at: http://localhost:8080"
	@echo "Username: admin, Password: admin"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "Airflow started! Use 'make logs' to see output or 'make shell' to access container."

.PHONY: down
down:
	@echo "Stopping Airflow containers..."
	docker-compose -f $(COMPOSE_FILE) down
	@echo "Airflow stopped!"

.PHONY: logs
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: shell
shell:
	@echo "Opening shell in Airflow container..."
	docker exec -it $(DOCKER_CONTAINER) /bin/bash

.PHONY: restart
restart: down up

# Development Commands
.PHONY: test
test:
	@echo "Running tests in container..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow-test pytest tests/ -v

.PHONY: test-watch
test-watch:
	@echo "Running tests in watch mode..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow-test python -m pytest_watch tests/

.PHONY: lint
lint:
	@echo "Running linting checks..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow-test flake8 dags/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "Linting complete!"

.PHONY: format
format:
	@echo "Formatting code..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow-test black dags/ tests/
	docker-compose -f $(COMPOSE_FILE) run --rm airflow-test isort dags/ tests/
	@echo "Code formatting complete!"

.PHONY: clean
clean:
	@echo "Cleaning up..."
	docker-compose -f $(COMPOSE_FILE) down --volumes --remove-orphans
	docker system prune -f
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

# Airflow Commands (aliases and specific commands)
.PHONY: airflow-start
airflow-start: up

.PHONY: airflow-stop
airflow-stop: down

.PHONY: airflow-init
airflow-init:
	@echo "Initializing Airflow database..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow airflow db migrate
	docker-compose -f $(COMPOSE_FILE) run --rm airflow airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com \
		--password admin

.PHONY: airflow-test
airflow-test:
	@echo "Testing DAG syntax and imports..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow-test python -c "import sys; sys.path.insert(0, '/app'); from dags import *; print('✓ All DAGs imported successfully')"

.PHONY: airflow-list
airflow-list:
	@echo "Listing all DAGs..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow airflow dags list

.PHONY: airflow-web
airflow-web:
	@echo "Airflow webserver should be available at: http://localhost:8080"
	@echo "Username: admin, Password: admin"
	@echo "If not running, use 'make up' to start Airflow"

# Database Commands
.PHONY: db-migrate
db-migrate:
	@echo "Running database migrations..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow airflow db migrate

.PHONY: db-reset
db-reset:
	@echo "Resetting Airflow database..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow airflow db reset --yes
	$(MAKE) airflow-init

# Utility Commands
.PHONY: status
status:
	@echo "Container status:"
	docker-compose -f $(COMPOSE_FILE) ps

.PHONY: check-deps
check-deps:
	@echo "Checking dependencies..."
	docker-compose -f $(COMPOSE_FILE) run --rm airflow-test pip check
	@echo "Dependency check complete!"

# Quick development setup
.PHONY: setup
setup: build airflow-init
	@echo "Development environment setup complete!"
	@echo "Run 'make up' to start Airflow"
	@echo "Then visit http://localhost:8080 (admin/admin)"
