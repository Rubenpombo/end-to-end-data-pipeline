# Single entry point for the demo: infrastructure, tests and quality checks.
DOCKER_COMPOSE := $(shell command -v docker-compose >/dev/null 2>&1 && echo "docker-compose" || echo "docker compose")
PYTEST := $(if $(wildcard .venv/bin/pytest),.venv/bin/pytest,pytest)
RUFF := $(if $(wildcard .venv/bin/ruff),.venv/bin/ruff,ruff)
YAMLLINT := $(if $(wildcard .venv/bin/yamllint),.venv/bin/yamllint,yamllint)

.PHONY: up down build ps logs test test-integration lint stream-local

up: ## Start the full stack (Kafka, Airflow, Spark, Cassandra, observability)
	$(DOCKER_COMPOSE) up -d

down: ## Stop the stack
	$(DOCKER_COMPOSE) down

build: ## Build custom images (Spark)
	$(DOCKER_COMPOSE) build

ps: ## Show service status
	$(DOCKER_COMPOSE) ps

logs: ## Tail logs of all services
	$(DOCKER_COMPOSE) logs -f

test: ## Run unit tests (no external services needed, same subset as CI)
	$(PYTEST) -m "not integration"

test-integration: ## Run integration tests (requires the stack up and internet)
	$(PYTEST) -m integration

lint: ## Run Ruff and yamllint
	$(RUFF) check .
	$(YAMLLINT) .

stream-local: ## Run the Spark streaming job on the host instead of in Docker
	CASSANDRA_HOST=localhost KAFKA_HOST=localhost:9092 SPARK_MASTER_URL=local[*] python3 spark_stream.py
