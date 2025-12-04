# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-04

### Added

- **Parallel Batch Downloading**: `fext batch` now supports downloading multiple extensions simultaneously.
- **CLI Argument**: Added `-w` / `--workers` flag to `fext batch` to control the number of concurrent downloads (default: 4).
- **Makefile Target**: Added `make test-batch-cli` for smoke testing batch downloads without pytest.
- **Integration Tests**: Added `tests/integration/test_batch_parallel.py` to verify parallel execution performance.

### Changed

- **Performance**: Refactored `BatchProcessor` to use `concurrent.futures.ThreadPoolExecutor` for improved speed when processing large batch files.
- **Documentation**: Updated `README.md` and `ROADMAP.md` to reflect parallel batch capabilities.

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
