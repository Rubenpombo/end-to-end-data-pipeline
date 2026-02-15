# Makefile for End-to-End Data Pipeline

# Variables
VENV_NAME = venv
PYTHON = $(VENV_NAME)/bin/python
PIP = $(VENV_NAME)/bin/pip
DOCKER_COMPOSE = docker-compose

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make up                - Start Docker containers"
	@echo "  make down              - Stop Docker containers"
	@echo "  make install           - Create virtual environment and install dependencies"
	@echo "  make test              - Run unit tests"
	@echo "  make airflow-activate  - Unpause the Airflow DAG (waits for scheduler)"
	@echo "  make stream            - Run the Spark streaming job (blocking)"
	@echo "  make all               - Setup environment, start containers, run tests, and activate airflow"
	@echo "  make clean             - Remove virtual environment and temporary files"

.PHONY: up
up:
	$(DOCKER_COMPOSE) up --build -d

.PHONY: down
down:
	$(DOCKER_COMPOSE) down

.PHONY: install
install:
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	$(PIP) install -r requirements.txt

.PHONY: test
test:
	$(PYTHON) -m unittest discover -s tests

.PHONY: airflow-activate
airflow-activate:
	@./script/wait_for_scheduler.sh
	docker exec scheduler airflow dags unpause user_automation
	@echo "DAG 'user_automation' unpaused."

.PHONY: stream
stream:
	$(PYTHON) spark_stream.py

.PHONY: restart
restart: down up

.PHONY: clean
clean:
	rm -rf $(VENV_NAME)
	rm -rf __pycache__
	rm -rf .pytest_cache
	# $(DOCKER_COMPOSE) down -v --remove-orphans # Uncomment to remove volumes (DATA LOSS WARNING)

.PHONY: all
all: install up test airflow-activate
	@echo "Pipeline initialized successfully."
	@echo "Run 'make stream' to start the data processing."
