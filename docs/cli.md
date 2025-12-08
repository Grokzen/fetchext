# CLI Reference

The `fetchext` CLI (command: `fext`) provides a comprehensive suite of tools for downloading, analyzing, and managing browser extensions.

## Basic Usage

```bash
fext <command> [options]
```

## Commands

### `download`

Download an extension from a web store.

```bash
fext download <browser> <url> [options]
```

**Aliases:** `d`

**Arguments:**

* `browser`: The target browser store. Supported values:
  * `chrome` (alias: `c`)
  * `edge` (alias: `e`)
  * `firefox` (alias: `f`)
* `url`: The full URL of the extension page.

**Options:**

* `-o, --output-dir <dir>`: Directory to save the downloaded file (default: current directory).
* `-m, --save-metadata`: Save extension metadata (ID, version, name) to a JSON file.
* `-x, --extract`: Automatically extract the extension contents to a folder.
* `--quiet`: Suppress output.
* `--verbose`: Enable verbose logging.

**Examples:**

```bash
# Download Chrome extension
fext download chrome https://chromewebstore.google.com/detail/...

# Download and extract
fext download firefox https://addons.mozilla.org/... --extract

# Save metadata
fext download edge https://microsoftedge.microsoft.com/... --save-metadata
```

### `search`

Search for extensions in a web store (currently supports Firefox).

```bash
fext search <browser> <query>
```

**Aliases:** `s`

**Example:**

```bash
fext search firefox "adblock"
```

### `inspect`

Inspect the metadata (manifest) of a downloaded extension file.

```bash
fext inspect <file>
```

**Aliases:** `i`

**Example:**

```bash
fext inspect ublock-origin.crx
```

### `extract`

Extract an existing extension file (`.crx`, `.xpi`) to a directory.

```bash
fext extract <file> [-o <output_dir>]
```

**Aliases:** `x`

**Example:**

```bash
fext extract ublock-origin.crx -o ./extracted
```

### `batch`

Download multiple extensions from a batch file.

```bash
fext batch <file> [-o <output_dir>] [-w <workers>]
```

**Aliases:** `b`

**Options:**

* `-w, --workers <n>`: Number of parallel downloads (default: 4).

**Batch File Format:**

```text
# Format: <browser> <url_or_id>
chrome aicmkgpgakddgnaphhhpliifpcfhicfo
firefox https://addons.mozilla.org/en-US/firefox/addon/postman_interceptor/
```

### `scan`

Scan an extension for known vulnerable third-party libraries (e.g., jQuery, Lodash).

```bash
fext scan <file> [--json]
```

**Example:**

```bash
fext scan ublock-origin.crx
```

### `report`

Generate a comprehensive Markdown report for an extension.

```bash
fext report <file> [-o <output_file>]
```

**Example:**

```bash
fext report ublock-origin.crx
```

### `convert`

Convert extensions between formats.

```bash
fext convert <input> --to <format> [-o <output>]
```

**Supported Formats:** `zip`

**Example:**

```bash
fext convert ublock-origin.crx --to zip
```

### `stats`

Analyze a directory of extensions for aggregate statistics.

```bash
fext stats <directory>
```

### `explain`

Get a detailed explanation and risk assessment for a specific permission.

```bash
fext explain <permission>
```

**Example:**

```bash
fext explain tabs
```

### `timeline`

Visualize the modification timeline of files within an extension.

```bash
fext timeline <file>
```

### `graph`

Generate a dependency graph of internal files.

```bash
fext graph <file> [-o <output.dot>]
```

### `optimize`

Losslessly compress images within an extension directory.

```bash
fext optimize <directory> [-q <quality>]
```

### `tutorial`

Launch the interactive TUI tutorial.

```bash
fext tutorial
```

### `setup`

Run the interactive configuration wizard.

```bash
fext setup
```

### `config`

Manage configuration settings.

```bash
fext config [get|set|list] [key] [value]
```

### `clean`

Clean up cache and temporary files.

```bash
fext clean [--dry-run] [--force] [--all]
```
