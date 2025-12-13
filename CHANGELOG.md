# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.3.0] - 2025-12-10

### Added

- **Visual Diff**: Added `fext diff --visual` to generate interactive HTML reports showing side-by-side comparisons of modified files and images.
- **Permission Matrix**: Added `fext analyze permissions <directory>` to generate a cross-reference matrix of permissions across multiple extensions (JSON/CSV/Table).
- **Property-Based Testing**: Implemented advanced fuzz testing for `CrxDecoder` using `hypothesis` to ensure robustness against malformed CRX headers.

### Fixed

- **Inspector Robustness**: Refactored `ExtensionInspector` to gracefully handle malformed manifests and corrupt archives, preventing crashes in reporting and visualization tools.
- **Network Error Handling**: Improved handling of HTTP 403 (Access Denied) and 429 (Rate Limit) errors with actionable user feedback (e.g., suggesting VPN or config changes).

## [2.2.0] - 2025-12-10

### Added

- **HTML Reports**: Added `fext report --html` to generate interactive HTML reports with Chart.js visualizations for risk, complexity, and file distribution.
- **Badge Generator**: Added `fext badge` command to generate SVG badges (Shields.io style) for version, risk score, and license, suitable for READMEs.
- **Repository Grep**: Added `fext grep <pattern>` command to search for regex patterns across all downloaded extensions, including content within compressed archives (CRX/ZIP).
- **Custom Rules**: Added `fext scan --custom <rules.yaml>` to run user-defined regex rules against extension source code for specialized auditing.
- **Scalable History**: Migrated history tracking from a flat JSON file to a SQLite database (`history.db`) to support thousands of records and advanced querying.

## [2.1.0] - 2025-12-10

### Added

- **Git Integration**: Added `fext git init` command to initialize a git repository in an extension directory with a tailored `.gitignore`.
- **Update All**: Added `fext update --all` command to check and update all previously downloaded extensions in parallel.
- **License Scanner**: Added `fext audit scan --licenses` to detect open source licenses (MIT, Apache, GPL, etc.) in extension files.
- **Remote Config**: Added `fext config remote <url>` command to fetch and apply configuration from a remote URL.

## [2.0.0] - 2025-12-10

### Added

- **Extension Packer**: Added `fext pack <directory>` command to create signed CRX3 files from source code, automatically generating RSA keys if needed.
- **MV3 Migration Assistant**: Added `fext migrate <directory>` command to automate the conversion of Manifest V2 extensions to Manifest V3 (updating manifest, permissions, background scripts, CSP).
- **Plugin System Enhancements**: Added `pre_pack`, `post_pack`, `pre_migrate`, and `post_migrate` hooks to the plugin system, allowing custom logic during packing and migration.
- **TUI Dashboard**: Added a comprehensive dashboard to `fext ui` featuring repository statistics, risk distribution charts, and recent activity history.
- **AI Summarizer**: Added `fext analyze summary <file>` command to generate AI-powered summaries of extension functionality using OpenAI-compatible APIs.
- **AI Configuration**: Added `[ai]` section to `config.toml` for configuring API keys, providers, and models.
- **Code Beautifier**: Added `fext beautify <file>` command to format minified JavaScript and JSON files using `jsbeautifier`.
- **Similarity Search**: Added `fext similar <target> <repo>` command to find similar extensions using fuzzy hashing (`ppdeep`).
- **Smart Diff**: Enhanced `fext diff` with `--ignore-whitespace` flag and basic image comparison (dimensions, format).

### Changed

- **CLI Breaking Change**: Refactored `fext analyze` to use positional arguments instead of flags.
  - Old: `fext analyze --complexity <file>`
  - New: `fext analyze complexity <file>`
  - Affected subcommands: `complexity`, `entropy`, `domains`, `secrets`, `yara`.

## [1.9.0] - 2025-12-10

### Changed

- **Startup Time Optimization**: Implemented lazy loading for heavy dependencies (`rich`, `PIL`, `lizard`, `yara`, `textual`, `cryptography`) to significantly reduce CLI startup time.
- **Memory Optimization**: Refactored `secrets` scanner to stream file content line-by-line and `yara` scanner to extract large files (>10MB) to temporary storage, reducing memory footprint during analysis of large extensions.
- **TUI Polish**: Improved `fext ui` with asynchronous search and download operations (preventing UI freezes), added browser selection (Chrome, Firefox, Edge), and enhanced error handling.
- **Progress Bars**: Standardized progress bar styles across all long-running commands (downloads, batch processing, complexity/entropy/domain analysis) using `rich`.
- **Dependency Review**: Removed `tomli` dependency as the project now requires Python 3.11+ (which includes `tomllib`).

## [1.8.0] - 2025-12-10

### Added

- **Plugin System v2**: Enhanced plugin system with richer context (`config`, `args`) and control flow (cancellation, result modification).
- **New Hooks**: Added `post_extract`, `pre_analysis`, and `post_analysis` hooks.
- **Debug Mode**: Enhanced `-v` / `--verbose` output to include full HTTP request/response headers and status codes (with sensitive data redaction).
- **API Documentation**: Added `make docs-api` to generate HTML API documentation using `pdoc`.
- **Shell Completion**: Added generation of Bash and Zsh completion scripts (`docs/completions/`).
- **Exit Codes**: Standardized CLI exit codes (0=Success, 3=Network, 4=IO, etc.) for better scripting support.

## [1.7.0] - 2025-12-07

### Added

- **CLI Version Flag**: Added `--version` flag to the CLI to display the current version of the tool.
- **Resumable Downloads**: Implemented support for resuming interrupted downloads using HTTP `Range` headers.
- **Network Resilience**: Enhanced `download_file` to handle `416 Range Not Satisfiable` errors by automatically restarting the download.
- **Integrity Checking**: Added `--verify-hash <sha256>` flag to `download` command to verify file integrity after download.
- **Proxy Configuration**: Added support for configuring HTTP/HTTPS proxies via `[network.proxies]` in `config.toml`.
- **Disk Space Safety**: Added pre-flight checks to ensure sufficient disk space before downloading or extracting extensions.
- **Filename Sanitization**: Implemented filename sanitization to ensure cross-platform compatibility (Windows/macOS/Linux) by stripping illegal characters.

## [1.6.0] - 2025-12-07

### Added

- **Docs Deployment**: Added GitHub Actions workflow to automatically build and deploy documentation to GitHub Pages.
- **Unified Audit Report**: Added `fext report --json` to generate a comprehensive JSON report aggregating metadata, risk analysis, MV3 audit, complexity, entropy, domains, and secrets.
- **Documentation Refactor**: Split documentation into a slim `README.md` (Quick Start) and detailed `docs/` site (MkDocs).

### Changed

- **Performance Optimization**: Parallelized entropy and complexity analysis using `ProcessPoolExecutor` to improve performance on multi-core systems.
- **YARA Integration**: Updated `fext analyze --yara` to accept a directory of rule files, compiling them all for the scan.
- **Risk Scoring Tuning**: Refined risk analysis to detect and penalize dangerous permission combinations (e.g., `tabs` + `cookies` + `<all_urls>`).
- **False Positive Reduction**: Improved `SecretScanner` accuracy by filtering out common placeholders, low-entropy strings, and URLs from "Generic API Key" matches.
- **Python Compatibility**: Added `tomli` fallback for Python 3.10 compatibility (while maintaining 3.11+ target).

### Fixed

- **Testing**: Fixed test suite hangs/deadlocks in complexity and entropy tests by mocking `ProcessPoolExecutor` when using `pyfakefs`.

## [1.5.0] - 2025-12-07

### Changed

- **CLI Modularization**: Refactored the monolithic `cli.py` into a modular command structure under `src/fetchext/commands/`. This improves maintainability and extensibility.

## [1.4.0] - 2025-12-07

### Added

- **Timeline View**: Added `fext timeline <file>` command to visualize file modification times within an extension archive for forensic analysis.
- **Local Server**: Added `fext serve` command to host the local repository as a Chrome Update Server (HTTP).
- **Dependency Graph**: Added `fext graph <file>` command to generate DOT graphs of internal file dependencies.
- **Image Optimizer**: Added `fext optimize <directory>` command to losslessly compress PNG and JPEG images within an extension to reduce size.
- **Interactive Tutorial**: Added `fext tutorial` command to launch a TUI-based interactive guide for new users.

## [1.3.0] - 2025-12-06

### Added

- **Format Converter**: Added `fext convert` command to convert between extension formats (CRX -> ZIP, Directory -> ZIP).
- **Configuration Wizard**: Added `fext setup` command to interactively create or update the user configuration file.
- **Markdown Reports**: Added `fext report <file>` command to generate comprehensive Markdown reports including metadata, risk analysis, and file structure.
- **Local Update Server**: Added `fext update-manifest` command to generate `update.xml` (Chrome/Edge) and `updates.json` (Firefox) for self-hosted extensions.
- **Mirror Mode**: Added `fext mirror` command to synchronize a local directory with a list of extension IDs, supporting updates and pruning.
- **Dependency Scanner**: Added `fext scan` command to detect known vulnerable libraries (e.g., jQuery, Lodash) within extension source code.
- **Plugin Hooks**: Added support for Python-based pre/post-download hooks in `~/.config/fext/hooks`.
- **Rate Limiting**: Added `rate_limit_delay` configuration option to throttle network requests and prevent IP bans.
- **Interactive TUI**: Added `fext ui` command to launch a terminal-based user interface for browsing and downloading extensions.
- **Repository Statistics**: Added `fext stats` command to analyze local repository metrics (count, size, permissions, MV2/MV3 breakdown).
- **CSV Export**: Added `--csv` flag to `search` and `scan` commands for exporting results to spreadsheet-friendly format.
- **Man Page Generation**: Added `make docs` to generate standard man pages (`docs/man/fext.1`).
- **Shell Completion**: Added generation of Bash and Zsh completion scripts (`docs/completions/`).
- **Fuzz Testing**: Added `make fuzz` to run hypothesis-based fuzz tests for robust parsing.
- **Documentation Site**: Added MkDocs-based documentation site configuration and `make docs-build` target.
- **Signed Releases**: Added infrastructure for GPG signing of releases (`make sign`, `make release`).
- **Complexity Analysis**: Added `fext analyze --complexity` to calculate cyclomatic complexity of JavaScript files.
- **Locale Inspector**: Added `fext locales` command to inspect supported locales and message counts.
- **Docker Image**: Added `Dockerfile` and GitHub Actions workflow for containerized deployment.
- **Pre-commit Hook**: Added `.pre-commit-hooks.yaml` for integration with pre-commit.
- **Permission Explainer**: Added `fext explain <permission>` command to provide detailed descriptions and risk assessments for extension permissions.
- **Entropy Analysis**: Added `fext analyze --entropy <file>` to calculate Shannon entropy of files within an extension to detect obfuscation or packing.
- **Domain Extractor**: Added `fext analyze --domains <file>` to extract all URLs and domains from extension source code for network forensics.
- **YARA Rules**: Added `fext analyze --yara <rules_file>` to scan extension files against YARA rules for malware detection.
- **Config Management**: Added `fext config` subcommand to get, set, and list configuration values in `~/.config/fext/config.toml`.
- **Cache Management**: Added `fext clean` subcommand to remove build artifacts, caches, and temporary files.
- **CSP Auditor**: Added Content Security Policy analysis to `fext audit` to detect weak security configurations.
- **Secret Scanner**: Added `fext scan --secrets` to detect API keys and tokens (AWS, Google, Slack, Stripe) in extension source code.
- **History Tracking**: Added `fext history` command to view a log of downloaded and extracted extensions.
- **JSON Schema**: Added `fext schema <type>` command to output JSON schemas for configuration and reports.
- **Plugin Manager**: Added `fext plugin` command to list, install, enable, and disable Python-based hooks.

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
