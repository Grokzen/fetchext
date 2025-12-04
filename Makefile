.PHONY: setup run lint format clean build

VENV = .venv
PYTHON = python
PIP = pip

setup:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -e .
	$(VENV)/bin/pip install build ruff

run:
	$(PYTHON) -m fetchext.cli $(URL)

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

build:
	$(PYTHON) -m build

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf src/*.egg-info
	rm -rf dist
	rm -rf downloads/

test-downloads:
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

test-inspect:
	# Inspect the downloaded files (assumes test-downloads has run)
	fext inspect downloads/aicmkgpgakddgnaphhhpliifpcfhicfo.crx
	fext inspect downloads/nbjbemmokmdpdokpnbfpdfbikmhgilmc.crx
	fext inspect downloads/postman_interceptor-3.2.1.xpi

test-batch:
	# Test batch download
	fext batch tests/batch_list.txt -o downloads/batch_output/

ci: lint build test-downloads test-inspect test-batch
