# Project Roadmap & Ideas

## �️ v0.5.0: Robustness & Internals

- [ ] **Proper CRX Parsing**: Implement a robust CRX3 parser.
  - [ ] Remove the "find ZIP header" hack in `utils.py`.
  - [ ] Read CRX3 header (Magic `Cr24`, Version, Header Length) to correctly locate the ZIP payload.
  - [ ] Support reading large files without loading them entirely into memory (streaming).
- [ ] **Update Checker**: Add `fext check <file>` command.
  - [ ] Extract ID and Version from a local file.
  - [ ] Query the respective Web Store to check if a newer version is available.
- [ ] **Network Resilience**: Add retry logic with backoff.
  - [ ] Implement `tenacity` or custom retry loop for network requests in downloaders.

## ⚙️ v0.6.0: Configuration & Distribution

- [ ] **Config File**: Add support for a user configuration file (e.g., `~/.config/fext/config.toml`).
  - [ ] Allow setting default download directory, worker count, and behavior flags (e.g., always extract).
- [ ] **PyPI Publishing**: Create a GitHub Action workflow to publish to PyPI on tag creation.
- [ ] **Cross-Platform CI**: Add `windows-latest` and `macos-latest` to GitHub Actions matrix.

## 🧠 v0.7.0: Advanced Analysis

- [ ] **Manifest V3 Analysis**: Add specific checks for MV3 compatibility.
  - [ ] Warn if an extension is using deprecated MV2 features.
- [ ] **Permission Risk Scoring**: Analyze permissions and assign a "risk score" to the extension.
- [ ] **Library Mode**: Ensure `fetchext` can be imported and used easily as a library by other Python scripts.

## ✅ Completed

- [x] **Extract Command**: Add `fext extract <file>` subcommand.
- [x] **Auto-Extraction**: Add `--extract` / `-x` flag to `download` command.
- [x] **Metadata Sidecars**: Add `--save-metadata` flag.
- [x] **Rich Output**: Integrate `rich` library for beautiful console output.
- [x] **Progress Bars**: Integrate `tqdm` (replaced by `rich`) to show download progress.
- [x] **Parallel Batch Downloading**: Use `ThreadPoolExecutor` for concurrent batch downloads.
- [x] **Mocked File System**: Use `pyfakefs` in unit tests.
