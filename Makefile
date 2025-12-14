.PHONY: help setup install run lint format clean build docs docs-serve docs-build docs-api sign release test test-live test-all test-coverage fuzz test-legacy-downloads test-batch-cli ci

VENV = .venv
PYTHON ?= python3
PIP = pip
MARKDOWNLINT = npx markdownlint-cli@0.31.1

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Create virtual environment and install dependencies
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -e .
	$(VENV)/bin/pip install -r requirements-dev.txt

install: ## Install dependencies in the current environment
	$(PIP) install -e .
	$(PIP) install -r requirements-dev.txt

run: ## Run the CLI (usage: make run URL=...)
	$(PYTHON) -m fetchext.cli $(URL)

lint: ## Run all linters (Python and Markdown)
	$(PYTHON) -m ruff check .
	$(MARKDOWNLINT) "**/*.md"

format: ## Format code and fix lint errors
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .
	$(MARKDOWNLINT) "**/*.md" --fix

build: ## Build the package
	$(PYTHON) -m build

docs: ## Generate documentation assets (man pages, completions)
	$(PYTHON) scripts/gen_man.py
	$(PYTHON) scripts/gen_completion.py

docs-serve: ## Serve documentation locally
	$(PYTHON) -m mkdocs serve

docs-build: ## Build documentation site
	$(PYTHON) -m mkdocs build

docs-api: ## Generate API documentation
	$(PYTHON) -m pdoc -o docs/api src/fetchext

sign: ## Detach-sign the built artifacts
	gpg --detach-sign -a dist/*.whl
	gpg --detach-sign -a dist/*.tar.gz

release: build sign ## Upload to PyPI
	$(PYTHON) -m twine upload dist/*

clean: ## Clean up build artifacts and temporary files
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf src/*.egg-info
	rm -rf dist
	rm -rf downloads/
	rm -rf site/

test: ## Run unit and integration tests (skips live tests)
	$(PYTHON) -m pytest -m "not live" --verbosity=5 --show-capture=all

test-live: ## Run live tests (requires network)
	$(PYTHON) -m pytest -m "live" --verbosity=5 --show-capture=all

test-all: ## Run all tests
	$(PYTHON) -m pytest --verbosity=5 --show-capture=all

test-coverage: ## Run tests with coverage report
	$(PYTHON) -m pytest --verbosity=5 --show-capture=all --cov=src/fetchext --cov-report=term-missing

fuzz: ## Run fuzz tests
	$(PYTHON) -m pytest --verbosity=5 --show-capture=all tests/fuzz/

test-legacy-downloads: ## Run legacy download tests using fext CLI
	# Chrome (URL)
	fext download chrome https://chromewebstore.google.com/detail/postman-interceptor/aicmkgpgakddgnaphhhpliifpcfhicfo -o downloads/
	# Chrome (ID)
	fext download chrome aicmkgpgakddgnaphhhpliifpcfhicfo -o downloads/
	# Edge (URL)
	fext download edge https://microsoftedge.microsoft.com/addons/detail/postman-interceptor/nbjbemmokmdpdokpnbfpdfbikmhgilmc -o downloads/
	# Edge (ID)
	fext download edge nbjbemmokmdpdokpnbfpdfbikmhgilmc -o downloads/
	# Firefox (URL)
	fext download firefox https://addons.mozilla.org/en-US/firefox/addon/postman_interceptor/ -o downloads/

test-batch-cli: ## Run batch processing test
	fext batch tests/batch_list.txt -o downloads/batch_output/ --workers 4

ci: lint build test ## Run CI pipeline (lint, build, test)
