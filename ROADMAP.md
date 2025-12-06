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

- [ ] **Complexity Analysis**: Code quality metrics (Analysis).
  - [ ] Add `fext analyze --complexity <file>` to calculate cyclomatic complexity of JS files (detect obfuscation).
- [ ] **Locale Inspector**: Internationalization support (Analysis).
  - [ ] Add `fext locales <file>` to extract and list all supported locales and messages.
- [ ] **Docker Image**: Containerized deployment (Deployment).
  - [ ] Publish official `Dockerfile` and GHCR image for CI/CD usage.
- [ ] **Pre-commit Hook**: Developer workflow integration (Integration).
  - [ ] Add `.pre-commit-hooks.yaml` to allow using `fext audit` in pre-commit pipelines.
- [ ] **Permission Explainer**: Educational tooling (Docs).
  - [ ] Add `fext explain <permission>` to provide human-readable context for manifest permissions.

## 🔮 v1.2.0: Advanced Security & Forensics

*Focus: Malware detection and forensic analysis.*

- [ ] **Entropy Analysis**: Obfuscation detection (Analysis).
  - [ ] Add `fext analyze --entropy <file>` to detect high-entropy strings (potential packed code or secrets).
- [ ] **Domain Extractor**: Network forensics (Analysis).
  - [ ] Add `fext analyze --domains <file>` to extract all URLs and domains from source code.
- [ ] **YARA Rules**: Malware matching (Security).
  - [ ] Integrate `yara-python` to scan extensions against a database of malicious signatures.
- [ ] **Timeline View**: Forensic timeline (Analysis).
  - [ ] Add `fext timeline <file>` to show a chronological view of file modification times within the archive.
- [ ] **Hidden File Detector**: Steganography check (Security).
  - [ ] Scan for files hidden within images or other assets.

## ✅ Completed

- [x] **Extract Command**: Add `fext extract <file>` subcommand.
- [x] **Auto-Extraction**: Add `--extract` / `-x` flag to `download` command.
- [x] **Metadata Sidecars**: Add `--save-metadata` flag.
- [x] **Rich Output**: Integrate `rich` library for beautiful console output.
- [x] **Progress Bars**: Integrate `tqdm` (replaced by `rich`) to show download progress.
- [x] **Parallel Batch Downloading**: Use `ThreadPoolExecutor` for concurrent batch downloads.
- [x] **Mocked File System**: Use `pyfakefs` in unit tests.
