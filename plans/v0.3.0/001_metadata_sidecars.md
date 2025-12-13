# Plan: Metadata Sidecars

## Goal

Implement a `--save-metadata` flag for the `download` command that saves a JSON file alongside the downloaded extension containing metadata (timestamp, source, version, etc.).

## Analysis

- **Current State**: `fext download` downloads the file and exits. No extra info is saved.
- **Requirement**: Save `metadata.json` with:
  - Download timestamp
  - Source URL
  - Version
  - Name (optional but good)
  - ID

## Strategy

1. **CLI Update**: Add `--save-metadata` (and `-m` alias) to `src/fetchext/cli.py` for the `download` parser.
2. **Metadata Generation**:
    - Since `ChromeDownloader` and `EdgeDownloader` don't fetch metadata via API (they construct download URLs), we can't rely on the downloader to provide metadata *before* download.
    - We can rely on `ExtensionInspector` to parse the *downloaded* file to get internal metadata (Name, Version, ID).
    - We can generate "external" metadata (Timestamp, Source URL, Provider).
3. **Implementation Logic**:
    - In `cli.py`, after `downloader.download()` returns the `output_path`:
    - If `args.save_metadata` is True:
        - Initialize `ExtensionInspector(output_path)`.
        - Parse manifest.
        - Create dictionary:

            ```json
            {
              "id": "...",
              "name": "...",
              "version": "...",
              "source_url": "...",
              "download_timestamp": "2023-10-27T10:00:00Z",
              "filename": "..."
            }
            ```

        - Save to `{output_path}.json` (e.g., `ublock.crx.json`).

## Files to Modify

- `src/fetchext/cli.py`: Add argument and logic.
- `tests/cli/test_cli.py`: Add test for the flag.
- `tests/integration/test_download_flow.py`: Verify JSON file creation.

## Verification Plan

- Run `fext download chrome <url> --save-metadata`.
- Check if `.json` file exists.
- Validate JSON content.
- Run `make test`.
