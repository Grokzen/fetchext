# Project Roadmap & Ideas

## 🛠️ v0.5.0: Core Reliability & Configuration

- [x] **Proper CRX Parsing**: Implement a robust CRX3 parser (Internals).
  - [x] Remove the "find ZIP header" hack in `utils.py`.
  - [x] Read CRX3 header (Magic `Cr24`, Version, Header Length) to correctly locate the ZIP payload.
  - [x] Support reading large files without loading them entirely into memory (streaming).
- [x] **Network Resilience**: Add retry logic with backoff (Network).
  - [x] Implement `tenacity` or custom retry loop for network requests in downloaders.
- [x] **Config File**: Add support for a user configuration file (Config).
  - [x] Load settings from `~/.config/fext/config.toml` (e.g., default download dir, worker count).
- [x] **Verbose/Quiet Mode**: Add global logging control (CLI).
  - [x] Implement `-v` (debug) and `-q` (errors only) flags.
- [x] **User-Agent Rotation**: Avoid blocking (Network).
  - [x] Randomize User-Agent headers for requests to Web Stores.

## ⚙️ v0.6.0: Automation & Integration

*Focus: Making `fext` scriptable and embeddable.*

- [x] **Library Mode**: Decouple CLI from core logic (Architecture).
  - [x] Ensure `import fetchext` allows programmatic access to downloaders and parsers.
- [x] **JSON Output**: Machine-readable output (CLI).
  - [x] Add `--json` flag to `search`, `inspect`, and `check` commands.
- [x] **Update Checker**: Add `fext check <file_or_dir>` command (CLI).
  - [x] Extract ID/Version from local files and query Web Store for updates.
- [x] **PyPI Publishing**: Automated release workflow (CI/CD).
  - [x] Finalize build pipeline to publish to PyPI on tag creation.

## 🧠 v0.7.0: Deep Analysis

*Focus: Security research and inspection capabilities.*

- [x] **Source Preview**: List contents without extracting (CLI).
  - [x] Add `fext preview <file>` to show file structure tree using streaming parser.
- [x] **Manifest V3 Auditor**: Check MV3 compatibility (Analysis).
  - [x] Report on MV2 vs MV3 status and deprecated APIs.
- [x] **Diff Command**: Compare two versions (CLI).
  - [x] Add `fext diff <old.crx> <new.crx>` to show changed files and permissions.
- [x] **Permission Risk Scoring**: Analyze permissions (Analysis).
  - [x] Assign "Privacy Risk" score based on requested permissions.
- [x] **Signature Verification**: Verify CRX integrity (Security).
  - [x] Validate the cryptographic signature of the CRX file against its public key.

## 🏢 v0.8.0: Enterprise & Scale

*Focus: Managing local repositories and bulk workflows.*

- [x] **Local Update Server**: Generate update manifests (Enterprise).
  - [x] Create `update.xml` / `updates.json` for self-hosted extension updates.
- [x] **Mirror Mode**: Sync local folder with ID list (Workflow).
  - [x] Add `fext mirror <list_file>` to keep a local repository up to date.
- [x] **Dependency Scanner**: Scan for vulnerable libraries (Security).
  - [x] Check internal JS files for known vulnerable library signatures.
- [x] **Plugin Hooks**: Extensibility system (Architecture).
  - [x] Support pre/post-download hooks (e.g., virus scan, git commit).
- [x] **Rate Limiting**: Respect Web Store limits (Network).
  - [x] Add configurable request delays to prevent IP bans during bulk operations.

## 🖥️ v0.9.0: Reporting & Usability

*Focus: Enhanced user experience and data portability.*

- [x] **Interactive TUI**: Terminal User Interface (CLI).
  - [x] Add `fext ui` for browsing and downloading using `textual` or `rich`.
- [x] **Markdown Reports**: Audit summaries (Analysis).
  - [x] Add `fext report <file>` to generate a readable `REPORT.md` with metadata and risk scores.
- [x] **Configuration Wizard**: Interactive setup (CLI).
  - [x] Add `fext setup` to guide users through creating the config file.
- [x] **Format Converter**: Repackaging tools (Core).
  - [x] Add `fext convert` to switch between raw source, CRX, and ZIP formats.
- [x] **Repository Statistics**: Local repo insights (Analysis).
  - [x] Add `fext stats` to visualize storage usage and permission trends.
- [x] **CSV Export**: Data portability (CLI).
  - [x] Add `--csv` flag to `search` and `scan` commands for spreadsheet integration.

## 🚀 v1.0.0: Stability & Production

*Focus: Hardening, performance, and final polish.*

- [x] **Man Page Generation**: Standard Linux documentation (Docs).
  - [x] Generate `man` pages for distribution packaging using `argparse-manpage` or similar.
- [x] **Shell Completion**: Native shell integration (CLI).
  - [x] Generate auto-completion scripts for Bash, Zsh, and Fish.
- [x] **Fuzz Testing**: Robustness verification (Quality).
  - [x] Implement fuzz testing for the CRX parser to handle malformed files.
- [x] **Documentation Site**: Comprehensive guides (Docs).
  - [x] Publish a static documentation site (MkDocs) to GitHub Pages.
- [x] **Signed Releases**: Supply chain security (Security).
  - [x] Implement Sigstore or GPG signing for PyPI packages and git tags.

## 🔬 v1.1.0: Advanced Analysis & Ecosystem

*Focus: Deep code inspection and developer integration.*

- [x] **Complexity Analysis**: Code quality metrics (Analysis).
  - [x] Add `fext analyze --complexity <file>` to calculate cyclomatic complexity of JS files (detect obfuscation).
- [x] **Locale Inspector**: Internationalization support (Analysis).
  - [x] Add `fext locales <file>` to extract and list all supported locales and messages.
- [x] **Docker Image**: Containerized deployment (Deployment).
  - [x] Publish official `Dockerfile` and GHCR image for CI/CD usage.
- [x] **Pre-commit Hook**: Developer workflow integration (Integration).
  - [x] Add `.pre-commit-hooks.yaml` to allow using `fext audit` in pre-commit pipelines.
- [x] **Permission Explainer**: Educational tooling (Docs).
  - [x] Add `fext explain <permission>` to provide human-readable context for manifest permissions.

## 🔮 v1.2.0: Advanced Forensics & Security

*Focus: Malware detection and forensic analysis.*

- [x] **Entropy Analysis**: Obfuscation detection (Analysis).
  - [x] Add `fext analyze --entropy <file>` to detect high-entropy strings (potential packed code or secrets).
- [x] **Domain Extractor**: Network forensics (Analysis).
  - [x] Add `fext analyze --domains <file>` to extract all URLs and domains from source code.
- [x] **YARA Rules**: Malware matching (Security).
  - [x] Integrate `yara-python` to scan extensions against a database of malicious signatures.
- [x] **Config Management**: CLI settings control (CLI).
  - [x] Add `fext config set <key> <value>` and `fext config get <key>` to manage settings.
- [x] **Cache Management**: Disk usage control (Core).
  - [x] Add `fext clean` to clear temporary download caches and build artifacts.

## 🛡️ v1.3.0: Developer Experience & Quality

*Focus: Deep auditing and developer tools.*

- [x] **CSP Auditor**: Security policy analysis (Analysis).
  - [x] Analyze `content_security_policy` for weak configurations (e.g., `unsafe-eval`).
- [x] **Secret Scanner**: Credential leakage detection (Security).
  - [x] Scan source code for potential API keys, tokens, and private keys using regex patterns.
- [x] **History Tracking**: Audit logs (CLI).
  - [x] Add `fext history` to view a local log of downloaded and extracted extensions and actions.
- [x] **JSON Schema**: Output standardization (Core).
  - [x] Publish and validate against JSON schemas for all `--json` command outputs.
- [x] **Plugin Manager**: Extension system (Ecosystem).
  - [x] Add `fext plugin` to manage Python-based hooks easily.

## 📊 v1.4.0: Visualization & Serving

*Focus: Data visualization and local hosting.*

- [x] **Timeline View**: Forensic timeline (Analysis).
  - [x] Add `fext timeline <file>` to visualize file modification times within the archive.
- [x] **Local Server**: Simple hosting (CLI).
  - [x] Add `fext serve` to host the local repository as a Chrome Update Server (HTTP).
- [x] **Dependency Graph**: Internal structure (Analysis).
  - [x] Generate DOT/Graphviz graphs of internal file dependencies/imports.
- [x] **Image Optimizer**: Asset reduction (Core).
  - [x] Add `fext optimize` to strip metadata from extension images to save space.
- [x] **Interactive Tutorial**: Onboarding (Docs).
  - [x] Add `fext tutorial` TUI walkthrough to teach users how to use the tool.

## 🧹 v1.5.0: Architecture Cleanup

*Focus: Refactoring and code hygiene.*

- [x] **CLI Modularization**: Split monolithic `cli.py` (Architecture).
  - [x] Refactor `cli.py` to use a command pattern, moving subcommands into `src/fetchext/commands/`.
- [x] **Unified Exception Handling**: Error management (Core).
  - [x] Create `src/fetchext/exceptions.py` and implement a custom exception hierarchy for consistent error reporting.
- [x] **Config Validation**: Robustness (Config).
  - [x] Add schema validation for `config.toml` on load to prevent runtime errors from typos.
- [x] **Path Standardization**: Code quality (Core).
  - [x] Audit codebase to ensure `pathlib.Path` is used exclusively (remove any lingering `os.path`).
- [x] **Logging Standardization**: Observability (Core).
  - [x] Review and standardize logging levels and formats across all modules using `rich`.

## 🛡️ v1.6.0: Security & Analysis Consolidation

*Focus: Hardening security tools and analysis reporting.*

- [x] **Unified Audit Report**: Reporting (Analysis).
  - [x] Create a single JSON schema/report that combines risk, secrets, and MV3 audit results.
- [x] **False Positive Reduction**: Accuracy (Security).
  - [x] Tune secret scanner regexes to reduce false positives for common patterns.
- [x] **Performance Optimization**: Speed (Analysis).
  - [x] Optimize `entropy` and `complexity` calculations for large extensions (parallel processing).
- [x] **YARA Integration**: Flexibility (Security).
  - [x] Allow `fext analyze --yara` to accept a directory of rule files, not just a single file.
- [x] **Risk Scoring Tuning**: Accuracy (Analysis).
  - [x] Refine the risk scoring algorithm to account for permission combinations (e.g., `tabs` + `http://*/*`).

## 🌐 v1.7.0: Network & Download Robustness

*Focus: Reliability and network features.*

- [x] **Resumable Downloads**: Reliability (Network).
  - [x] Support `Range` headers to resume interrupted downloads for large files.
- [x] **Integrity Checking**: Security (Core).
  - [x] Verify SHA256 of downloaded files against the Web Store (if available) or internal hash.
- [x] **Proxy Configuration**: Network (Config).
  - [x] Add explicit proxy support (`http`, `https`) to `config.toml`.
- [x] **Disk Space Safety**: Reliability (Core).
  - [x] Check free disk space before starting download or extraction to prevent partial writes.
- [x] **Filename Sanitization**: Compatibility (Core).
  - [x] Ensure downloaded filenames are safe on all OSes (Windows/macOS/Linux) by stripping illegal characters.

## 🧪 v1.8.0: Testing & Quality Assurance

*Focus: Test coverage and developer tools.*

- [x] **Plugin System v2**: Extensibility (Architecture).
  - [x] Enhance plugin hooks to receive full context (config, args) and allow modifying behavior.
- [x] **Debug Mode**: Developer Experience (CLI).
  - [x] Enhance `-v` output to dump full HTTP headers and response codes for debugging.
- [x] **API Documentation**: Docs (Core).
  - [x] Generate API documentation for `fetchext.core` using `pdoc` or similar.
- [x] **Shell Completion**: Usability (CLI).
  - [x] Verify and improve generated shell completion scripts for zsh and bash.
- [x] **Exit Codes**: Scripting (CLI).
  - [x] Standardize and document specific exit codes (e.g., 1=Generic, 2=Network, 3=IO).

## 🚀 v1.9.0: Performance & Polish

*Focus: Optimization and user experience.*

- [x] **Startup Time**: Performance (Core).
  - [x] Optimize import times by using lazy imports for heavy modules (e.g., `rich`, `Pillow`).
- [x] **Memory Usage**: Performance (Core).
  - [x] Profile and reduce memory footprint during extraction and analysis of large archives.
- [x] **TUI Polish**: UX (CLI).
  - [x] Improve `fext ui` responsiveness, error handling, and navigation.
- [x] **Progress Bars**: UX (CLI).
  - [x] Standardize progress bar styles and behavior across all long-running commands.
- [x] **Dependency Review**: Maintenance (Core).
  - [x] Audit and prune unused or redundant dependencies to keep the package lightweight.

## 🧠 v2.0.0: Intelligence & Insight

*Focus: AI integration, deeper understanding, and visual improvements.*

- [x] **AI Summarizer**: Code intent analysis (Analysis).
  - [x] Add `fext analyze --summary <file>` to generate a natural language summary of the extension's functionality using a local LLM or API.
- [x] **Code Beautifier**: Deobfuscation helper (Core).
  - [x] Add `fext beautify <file>` to format minified JavaScript and JSON files for better readability.
- [x] **Similarity Search**: Code reuse detection (Analysis).
  - [x] Add `fext similar <file>` to find other extensions in the local repository with high code similarity (using fuzzy hashing).
- [x] **Smart Diff**: Visual comparison (CLI).
  - [x] Enhance `fext diff` to visually compare changed images/assets and support "ignore whitespace" for code diffs.
- [ ] **TUI Dashboard**: Visual Analytics (TUI).
  - [ ] Add a "Home" screen to `fext ui` displaying repository statistics (disk usage, risk distribution) using charts.

## 📦 v2.1.0: Lifecycle & Management

*Focus: Full lifecycle management and workflow automation.*

- [ ] **Extension Packer**: CRX creation (Core).
  - [ ] Add `fext pack <dir>` to create a signed CRX file from a source directory (reverse of extract).
- [ ] **Git Integration**: Version control (Workflow).
  - [ ] Add `fext git init` to automatically set up a git repo for a downloaded extension with proper `.gitignore`.
- [ ] **Update All**: Bulk maintenance (Workflow).
  - [ ] Add `fext update --all` to check and update all extensions currently tracked in the local repository/history.
- [ ] **License Scanner**: Legal compliance (Analysis).
  - [ ] Add `fext scan --licenses` to identify open source licenses in extension files.
- [ ] **Remote Config**: Centralized management (Config).
  - [ ] Add `fext config --remote <url>` to load configuration from a remote URL (useful for teams).

## 📊 v2.2.0: Reporting & Ecosystem

*Focus: Advanced reporting, searching, and scalability.*

- [ ] **HTML Report**: Rich reporting (Reporting).
  - [ ] Add `fext report --html` to generate a standalone, interactive HTML report with charts and graphs.
- [ ] **Badge Generator**: Status indicators (Docs).
  - [ ] Add `fext badge <file>` to generate SVG badges for risk scores, version, and license for use in READMEs.
- [ ] **Repo Grep**: Deep search (Analysis).
  - [ ] Add `fext grep <pattern>` to search for string patterns across the source code of *all* downloaded extensions.
- [ ] **Custom Rules**: Lightweight analysis (Analysis).
  - [ ] Support a YAML-based rules engine for defining custom scan patterns without writing full Python plugins.
- [ ] **Scalable History**: Performance (Core).
  - [ ] Migrate `history` tracking to an optional SQLite backend to support repositories with thousands of extensions.

## ✅ Completed

- [x] **Extract Command**: Add `fext extract <file>` subcommand.
- [x] **Auto-Extraction**: Add `--extract` / `-x` flag to `download` command.
- [x] **Metadata Sidecars**: Add `--save-metadata` flag.
- [x] **Rich Output**: Integrate `rich` library for beautiful console output.
- [x] **Progress Bars**: Integrate `tqdm` (replaced by `rich`) to show download progress.
- [x] **Parallel Batch Downloading**: Use `ThreadPoolExecutor` for concurrent batch downloads.
- [x] **Mocked File System**: Use `pyfakefs` in unit tests.
