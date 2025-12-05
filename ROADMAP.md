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
- [ ] **Manifest V3 Auditor**: Check MV3 compatibility (Analysis).
  - [ ] Report on MV2 vs MV3 status and deprecated APIs.
- [ ] **Diff Command**: Compare two versions (CLI).
  - [ ] Add `fext diff <old.crx> <new.crx>` to show changed files and permissions.
- [ ] **Permission Risk Scoring**: Analyze permissions (Analysis).
  - [ ] Assign "Privacy Risk" score based on requested permissions.
- [ ] **Signature Verification**: Verify CRX integrity (Security).
  - [ ] Validate the cryptographic signature of the CRX file against its public key.

## 🏢 v0.8.0: Enterprise & Scale

*Focus: Managing local repositories and bulk workflows.*

- [ ] **Local Update Server**: Generate update manifests (Enterprise).
  - [ ] Create `update.xml` / `updates.json` for self-hosted extension updates.
- [ ] **Mirror Mode**: Sync local folder with ID list (Workflow).
  - [ ] Add `fext mirror <list_file>` to keep a local repository up to date.
- [ ] **Dependency Scanner**: Scan for vulnerable libraries (Security).
  - [ ] Check internal JS files for known vulnerable library signatures.
- [ ] **Plugin Hooks**: Extensibility system (Architecture).
  - [ ] Support pre/post-download hooks (e.g., virus scan, git commit).

## 🖥️ v0.9.0: Interactive & Ecosystem

*Focus: Enhanced user experience and deployment options.*

- [ ] **Interactive TUI**: Terminal User Interface (CLI).
  - [ ] Add `fext ui` for browsing and downloading using `textual` or `rich`.
- [ ] **Docker Support**: Official Container Image (DevOps).
  - [ ] Provide a `Dockerfile` and publish to GHCR for easy CI usage.
- [ ] **Configuration Wizard**: Interactive setup (CLI).
  - [ ] Add `fext setup` to guide users through creating the config file.
- [ ] **Format Converter**: Repackaging tools (Core).
  - [ ] Add `fext convert` to switch between raw source, CRX, and ZIP formats.
- [ ] **Repository Statistics**: Local repo insights (Analysis).
  - [ ] Add `fext stats` to visualize storage usage and permission trends.

## ✅ Completed

- [x] **Extract Command**: Add `fext extract <file>` subcommand.
- [x] **Auto-Extraction**: Add `--extract` / `-x` flag to `download` command.
- [x] **Metadata Sidecars**: Add `--save-metadata` flag.
- [x] **Rich Output**: Integrate `rich` library for beautiful console output.
- [x] **Progress Bars**: Integrate `tqdm` (replaced by `rich`) to show download progress.
- [x] **Parallel Batch Downloading**: Use `ThreadPoolExecutor` for concurrent batch downloads.
- [x] **Mocked File System**: Use `pyfakefs` in unit tests.
