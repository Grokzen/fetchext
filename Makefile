.PHONY: setup run lint format clean build docs

VENV = .venv
PYTHON ?= python3
PIP = pip

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -e .
	$(VENV)/bin/pip install -r requirements-dev.txt

run:
	$(PYTHON) -m fetchext.cli $(URL)

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

build:
	$(PYTHON) -m build

docs:
	$(PYTHON) scripts/gen_man.py
	$(PYTHON) scripts/gen_completion.py

docs-serve:
	$(PYTHON) -m mkdocs serve

docs-build:
	$(PYTHON) -m mkdocs build

sign:
	# Detach-sign the built artifacts
	gpg --detach-sign -a dist/*.whl
	gpg --detach-sign -a dist/*.tar.gz

release: build sign
	# Upload to PyPI
	$(PYTHON) -m twine upload dist/*

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf src/*.egg-info
	rm -rf dist
	rm -rf downloads/

test:
	$(PYTHON) -m pytest -m "not live"

test-live:
	$(PYTHON) -m pytest -m "live"

test-all:
	$(PYTHON) -m pytest

test-coverage:
	$(PYTHON) -m pytest --cov=src/fetchext --cov-report=term-missing

fuzz:
	$(PYTHON) -m pytest tests/fuzz/

# Legacy tests (kept for reference, but CI should use pytest)
test-legacy-downloads:
	# Test downloads postman extensions to validate all three downloads works
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

test-batch-cli:
	# Test batch processing using the CLI directly
	fext batch tests/batch_list.txt -o downloads/batch_output/ --workers 4

ci: lint build test
