.PHONY: setup train-model test up down logs load-test docker-build lint migrate verify verify-terraform check pdf

PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@test -f .env || cp .env.example .env
	@echo "Setup complete. Activate: source $(VENV)/bin/activate"

train-model:
	$(PY) scripts/train_model.py

test:
	$(PY) -m pytest tests/ -v --tb=short

lint:
	$(VENV)/bin/ruff check app tests scripts
	$(VENV)/bin/ruff format --check app tests scripts

up:
	docker compose up --build -d
	@echo "API: http://localhost:8000/docs"

down:
	docker compose down

logs:
	docker compose logs -f api

load-test:
	chmod +x scripts/load_test_hey.sh
	./scripts/load_test_hey.sh

docker-build:
	docker compose build

migrate:
	$(VENV)/bin/alembic upgrade head

verify:
	chmod +x scripts/verify_local.sh
	./scripts/verify_local.sh

verify-terraform:
	chmod +x scripts/verify_terraform.sh
	./scripts/verify_terraform.sh

check: lint test verify-terraform
	@echo "Static checks passed. For full smoke test: make up && make verify"

pdf:
	$(PY) scripts/generate_project_pdf.py
