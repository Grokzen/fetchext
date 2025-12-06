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
- [ ] **Local Server**: Simple hosting (CLI).
  - [ ] Add `fext serve` to host the local repository as a Chrome Update Server (HTTP).
- [ ] **Dependency Graph**: Internal structure (Analysis).
  - [ ] Generate DOT/Graphviz graphs of internal file dependencies/imports.
- [ ] **Image Optimizer**: Asset reduction (Core).
  - [ ] Add `fext optimize` to strip metadata from extension images to save space.
- [ ] **Interactive Tutorial**: Onboarding (Docs).
  - [ ] Add `fext tutorial` TUI walkthrough to teach users how to use the tool.

## 🌐 v1.5.0: Intelligence & Web

*Focus: AI integration and web-based interaction.*

- [ ] **AI Summarizer**: Code intent analysis (Analysis).
  - [ ] Add `fext analyze --summary <file>` to generate a natural language summary of the extension's functionality using a local LLM or API.
- [ ] **Code Beautifier**: Deobfuscation helper (Core).
  - [ ] Add `fext beautify <file>` to format minified JavaScript and JSON files for better readability.
- [ ] **Similarity Search**: Code reuse detection (Analysis).
  - [ ] Add `fext similar <file>` to find other extensions in the local repository with high code similarity (using fuzzy hashing).
- [ ] **Asset Diff**: Visual comparison (Analysis).
  - [ ] Enhance `fext diff` to visually compare changed images and assets between versions.
- [ ] **Badge Generator**: Status indicators (Docs).
  - [ ] Add `fext badge <file>` to generate SVG badges for risk scores, version, and license for use in READMEs.

## 📦 v1.6.0: Lifecycle & Integration

*Focus: Full lifecycle management and external integration.*

- [ ] **Extension Packer**: CRX creation (Core).
  - [ ] Add `fext pack <dir>` to create a signed CRX file from a source directory (reverse of extract).
- [ ] **License Scanner**: Legal compliance (Analysis).
  - [ ] Add `fext scan --licenses` to identify open source licenses in extension files.
- [ ] **Git Integration**: Version control (Workflow).
  - [ ] Add `fext git init` to automatically set up a git repo for a downloaded extension with proper `.gitignore`.
- [ ] **Remote Config**: Centralized management (Config).
  - [ ] Add `fext config --remote <url>` to load configuration from a remote URL.
- [ ] **HTML Report**: Rich reporting (Reporting).
  - [ ] Add `fext report --html` to generate a standalone, interactive HTML report with charts and graphs.

## ✅ Completed

- [x] **Extract Command**: Add `fext extract <file>` subcommand.
- [x] **Auto-Extraction**: Add `--extract` / `-x` flag to `download` command.
- [x] **Metadata Sidecars**: Add `--save-metadata` flag.
- [x] **Rich Output**: Integrate `rich` library for beautiful console output.
- [x] **Progress Bars**: Integrate `tqdm` (replaced by `rich`) to show download progress.
- [x] **Parallel Batch Downloading**: Use `ThreadPoolExecutor` for concurrent batch downloads.
- [x] **Mocked File System**: Use `pyfakefs` in unit tests.
