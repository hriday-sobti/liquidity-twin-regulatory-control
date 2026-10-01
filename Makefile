# Liquidity Twin Makefile
# Regulatory Liquidity Digital Twin, Control Graph and Reporting Compiler

.PHONY: help install dev db-up db-down migrate seed calculate controls reports test lint typecheck e2e verify demo clean

help:
	@echo "Liquidity Twin — Operations Manual"
	@echo "  make install     Install backend and frontend dependencies"
	@echo "  make dev         Launch backend and frontend in development mode"
	@echo "  make db-up       Spin up PostgreSQL container (if Docker available)"
	@echo "  make db-down     Stop PostgreSQL container"
	@echo "  make migrate     Run database migrations"
	@echo "  make seed        Seed synthetic bank events, entities, and rules"
	@echo "  make calculate   Execute regulatory liquidity calculations (NSFR & LCR)"
	@echo "  make controls    Execute 100+ automated control suite"
	@echo "  make reports     Compile PDF and XLSX regulatory reporting packs"
	@echo "  make test        Execute pytest test suite"
	@echo "  make lint        Run ruff linter and code formatter check"
	@echo "  make typecheck   Run mypy static type analysis"
	@echo "  make e2e         Run end-to-end API and UI smoke tests"
	@echo "  make verify      Run full verification pipeline (lint, test, calculations, controls, reports)"
	@echo "  make demo        Single-command demo setup and execution"
	@echo "  make clean       Purge temporary build files and caches"

install:
	python -m pip install -e ".[dev]"
	cd frontend && npm install

dev:
	python -m scripts.run_dev

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

migrate:
	python -m scripts.run_migrations

seed:
	python -m scripts.run_seed

calculate:
	python -m scripts.run_calculations

controls:
	python -m scripts.run_controls

reports:
	python -m scripts.compile_reports

test:
	pytest backend/tests -v

lint:
	ruff check backend

typecheck:
	mypy backend/app

e2e:
	python -m scripts.run_smoke_tests

verify: lint test calculate controls reports e2e
	@echo "ALL VERIFICATION CHECKS PASSED SUCCESSFULLY."

demo: seed calculate controls reports
	@echo "DEMO DATASET, CALCULATIONS, CONTROLS, AND REPORTS SUCCESSFULLY INITIALIZED."
	python -m scripts.run_dev

clean:
	python -c "import shutil, os, glob; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True)]; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', '.mypy_cache', '.ruff_cache', 'build', 'dist']]"
