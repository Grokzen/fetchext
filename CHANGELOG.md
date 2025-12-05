# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2025-12-05

### Added

- **Update Checker**: Added `check` subcommand to check for updates of local extension files against the Web Store.
- **JSON Output**: Added `--json` flag to `search` and `inspect` commands to output machine-readable JSON.
- **PyPI Publishing**: Added GitHub Actions workflow to automatically publish releases to PyPI on tag creation.

### Changed

- **Library Mode**: Refactored core logic into `src/fetchext/core.py` to allow programmatic usage of `fetchext` as a library.
- **Public API**: Exposed `download_extension`, `search_extension`, `inspect_extension`, `extract_extension`, and `batch_download` in `src/fetchext/__init__.py`.

## [0.5.0] - 2025-12-05

### Added

- **Proper CRX Parsing**: Implemented a robust CRX3 parser (`CrxDecoder`) and `PartialFileReader` to handle CRX files without loading them entirely into memory.
- **Network Resilience**: Added automatic retries with exponential backoff for network requests to handle transient failures (5xx errors, connection issues).
- **Config File**: Added support for a user configuration file (`~/.config/fext/config.toml`) to set default values for download directory, worker count, and flags.
- **Verbose/Quiet Mode**: Added `-v` / `--verbose` (DEBUG level) and `-q` / `--quiet` (ERROR level, no progress bars) flags for global logging control.
- **User-Agent Rotation**: Implemented random User-Agent rotation for network requests to avoid blocking by Web Stores.

## [0.3.0] - 2025-12-04

### Added

- **Extract Command**: Added `fext extract` subcommand to unzip existing extension files.
- **Auto-Extraction**: Added `--extract` / `-x` flag to `download` command to automatically unzip the downloaded extension.
- **Metadata Sidecars**: Added `--save-metadata` / `-m` flag to `download` command to save extension details (ID, name, version, source, timestamp) to a JSON file.
- **Rich Output**: Replaced `tqdm` and standard logging with `rich` for beautiful console output, progress bars, and tables.
- **Progress Bars**: Integrated `tqdm` to display progress bars for file downloads and batch processing.
- **Dependencies**: Added `rich` to `pyproject.toml` and `requirements-dev.txt`.
- **Parallel Batch Downloading**: `fext batch` now supports downloading multiple extensions simultaneously.
- **CLI Argument**: Added `-w` / `--workers` flag to `fext batch` to control the number of concurrent downloads (default: 4).
- **Makefile Target**: Added `make test-batch-cli` for smoke testing batch downloads without pytest.
- **Integration Tests**: Added `tests/integration/test_batch_parallel.py` to verify parallel execution performance.
- **Testing**: Added `pyfakefs` to `requirements-dev.txt` and integrated it into unit and integration tests to mock file system operations.

### Changed

- **Dependencies**: Replaced `tqdm` with `rich` in `pyproject.toml` and `requirements-dev.txt`.
- **Inspector**: Updated `inspect` command to display manifest data in a formatted table.
- **Search**: Updated `search` command (Firefox) to display results in a formatted table.
- **Batch Processing**: Updated `BatchProcessor` to show a main "Batch Progress" bar and disable individual file download bars during batch operations.
- **Downloaders**: Updated `ChromeDownloader`, `EdgeDownloader`, and `FirefoxDownloader` to support an optional `show_progress` argument.
- **Performance**: Refactored `BatchProcessor` to use `concurrent.futures.ThreadPoolExecutor` for improved speed when processing large batch files.
- **Documentation**: Updated `README.md` and `ROADMAP.md` to reflect parallel batch capabilities.
- **Testing**: Refactored unit and integration tests to use `pyfakefs` instead of real temporary files, improving test isolation and speed.

## [0.1.0] - 2025-12-04

### Added

- **Multi-Browser Support**: Core functionality to download extensions from Chrome Web Store, Microsoft Edge Add-ons, and Firefox Add-ons.
- **CLI**: Unified `fext` command-line interface with `download`, `batch`, and `inspect` subcommands.
- **Project Structure**: Adopted `src/` layout for better packaging and import isolation.
- **Testing**: Implemented a 4-level testing strategy (Unit, CLI, Integration, Live) using `pytest`.
- **CI/CD**: GitHub Actions workflow for automated linting, building, and testing on Python 3.11+.
- **Development Tools**: `Makefile` for common tasks (`setup`, `test`, `lint`, `format`, `build`).
- **Linting**: Enforced strict code quality with `ruff` (Python) and `markdownlint` (Markdown).
- **Inspector**: Basic `ExtensionInspector` to parse and display manifest data from downloaded `.crx` and `.xpi` files.
- **Documentation**: Comprehensive `README.md` and `copilot-instructions.md` for project context and agent guidelines.
