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
- [ ] **User-Agent Rotation**: Avoid blocking (Network).
  - [ ] Randomize User-Agent headers for requests to Web Stores.

## ⚙️ v0.6.0: Distribution & Integration

- [ ] **Update Checker**: Add `fext check <file>` command (CLI).
  - [ ] Extract ID and Version from a local file and query Web Store for updates.
- [ ] **Library Mode**: Ensure `fetchext` is import-friendly (Architecture).
  - [ ] Refactor `cli.py` logic into reusable service classes.
  - [ ] Add `__all__` exports to `__init__.py`.
- [ ] **JSON Output**: Machine-readable output (CLI).
  - [ ] Add `--json` flag to `search` and `inspect` commands for piping to `jq` or other tools.
- [ ] **PyPI Publishing**: Automated release workflow (CI/CD).
  - [ ] Create GitHub Action to publish to PyPI on tag creation.
- [ ] **Cross-Platform CI**: Expand testing matrix (CI/CD).
  - [ ] Add `windows-latest` and `macos-latest` to GitHub Actions.

## 🧠 v0.7.0: Insight & Security

- [ ] **Manifest V3 Analysis**: Check MV3 compatibility (Analysis).
  - [ ] Warn if an extension is using deprecated MV2 features.
- [ ] **Permission Risk Scoring**: Analyze permissions (Analysis).
  - [ ] Assign a "risk score" based on requested permissions (e.g., `<all_urls>`, `cookies`).
- [ ] **Source Preview**: List contents without extracting (CLI).
  - [ ] Add `fext preview <file>` to show file structure tree.
- [ ] **Dependency Audit**: Scan for vulnerable libraries (Security).
  - [ ] Basic check for known vulnerable JS library filenames or hashes.
- [ ] **Documentation Site**: Publish project docs (Docs).
  - [ ] Generate and publish MkDocs/Sphinx site to GitHub Pages.

## ✅ Completed

- [x] **Extract Command**: Add `fext extract <file>` subcommand.
- [x] **Auto-Extraction**: Add `--extract` / `-x` flag to `download` command.
- [x] **Metadata Sidecars**: Add `--save-metadata` flag.
- [x] **Rich Output**: Integrate `rich` library for beautiful console output.
- [x] **Progress Bars**: Integrate `tqdm` (replaced by `rich`) to show download progress.
- [x] **Parallel Batch Downloading**: Use `ThreadPoolExecutor` for concurrent batch downloads.
- [x] **Mocked File System**: Use `pyfakefs` in unit tests.
