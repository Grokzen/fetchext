# Project Roadmap & Ideas

## 🚀 v0.3.0: Inspection & UX Polish

- [x] **Rich Output**: Integrate `rich` library.
  - [x] Replace `print()` statements in `ExtensionInspector` with `rich.console.Console` and `rich.table.Table`.
  - [x] Style CLI logs and error messages.
- [x] **Metadata Sidecars**: Add `--save-metadata` flag.
  - [x] Save a `metadata.json` alongside the extension containing download timestamp, source URL, and version.

## 📦 v0.4.0: File Management & Utilities

- [x] **Auto-Extraction**: Add `--extract` / `-x` flag to `download` command.
  - [x] Automatically unzip the downloaded extension into a folder named after the extension ID or name.
- [x] **Extract Command**: Add `fext extract <file>` subcommand.
  - [x] Allow extracting existing `.crx` or `.xpi` files.

## 🔄 v0.5.0: Updates & Maintenance

- [ ] **Proper CRX Parsing**: Implement a robust CRX3 parser.
  - [ ] Remove the "find ZIP header" hack.
  - [ ] Read CRX3 header (Magic `Cr24`, Version, Header Length) to correctly locate the ZIP payload.
  - [ ] Support reading large files without loading them entirely into memory.
- [ ] **Update Checker**: Add `fext check <file>` command.
  - [ ] Extract ID and Version from a local file.
  - [ ] Query the respective Web Store to check if a newer version is available.
- [ ] **Windows/MacOS CI**: Add `windows-latest` and `macos-latest` to GitHub Actions.
- [ ] **PyPI Publishing**: Create a GitHub Action workflow to publish to PyPI on tag creation.

## ✅ Completed

- [x] **Progress Bars**: Integrate `tqdm` to show download progress.
- [x] **Parallel Batch Downloading**: Use `ThreadPoolExecutor` for concurrent batch downloads.
- [x] **Mocked File System**: Use `pyfakefs` in unit tests.
