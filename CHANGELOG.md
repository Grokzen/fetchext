# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Configuration Wizard**: Added `fext setup` command to interactively create or update the user configuration file.
- **Markdown Reports**: Added `fext report <file>` command to generate comprehensive Markdown reports including metadata, risk analysis, and file structure.
- **Local Update Server**: Added `fext update-manifest` command to generate `update.xml` (Chrome/Edge) and `updates.json` (Firefox) for self-hosted extensions.
- **Mirror Mode**: Added `fext mirror` command to synchronize a local directory with a list of extension IDs, supporting updates and pruning.
- **Dependency Scanner**: Added `fext scan` command to detect known vulnerable libraries (e.g., jQuery, Lodash) within extension source code.
- **Plugin Hooks**: Added support for Python-based pre/post-download hooks in `~/.config/fext/hooks`.
- **Rate Limiting**: Added `rate_limit_delay` configuration option to throttle network requests and prevent IP bans.
- **Interactive TUI**: Added `fext ui` command to launch a terminal-based user interface for browsing and downloading extensions.

## [0.7.0] - 2025-12-06

### Added

- **Source Preview**: Added `fext preview <file>` command to list extension contents without extracting.
- **Manifest V3 Auditor**: Added `fext audit <file>` command to check for MV3 compatibility and deprecated APIs.
- **Diff Command**: Added `fext diff <old> <new>` command to compare two extension versions.
- **Risk Analysis**: Added `fext risk <file>` command to analyze permission risks and assign a privacy score.
- **Signature Verification**: Added `fext verify <file>` command to cryptographically verify CRX3 signatures.

### Fixed

- **Build System**: Fixed `TypeError: canonicalize_version()` build error by upgrading `setuptools` requirement to `>=77.0`.
- **CI/CD**: Fixed CI test failures by adding missing `pytest-asyncio` dependency and fixing TUI test focus logic.
- **Logging**: Fixed a regression where the TUI module globally disabled logging, causing test failures in other modules.
- **Deprecations**: Resolved `setuptools` deprecation warnings by updating `pyproject.toml` to use SPDX license expression and removing deprecated classifiers.

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
