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
* `--verify-hash <sha256>`: Verify the downloaded file against a known SHA256 hash.
* `--quiet`: Suppress output.
* `--verbose`: Enable verbose logging. This includes full HTTP request/response headers (with sensitive data redacted) and status codes for debugging network issues.

> **Note:** Downloads are resumable. If a download is interrupted, running the command again will resume from where it left off.

### `search`

Search for extensions in a web store (currently supports Firefox).

```bash
fext search <browser> <query> [options]
```

**Aliases:** `s`

**Options:**

* `--json`: Output results as JSON.
* `--csv`: Output results as CSV.

### `inspect`

Inspect the metadata (manifest) of a downloaded extension file.

```bash
fext inspect <file> [options]
```

**Aliases:** `i`

**Options:**

* `--json`: Output results as JSON.

### `preview`

List the contents of an extension archive without extracting it.

```bash
fext preview <file>
```

**Aliases:** `p`

### `extract`

Extract an existing extension file (`.crx`, `.xpi`) to a directory.

```bash
fext extract <file> [-o <output_dir>]
```

**Aliases:** `x`

### `batch`

Download multiple extensions from a batch file.

```bash
fext batch <file> [-o <output_dir>] [-w <workers>]
```

**Aliases:** `b`

**Options:**

* `-w, --workers <n>`: Number of parallel downloads (default: 4).

### `audit`

Audit an extension for Manifest V3 compatibility and deprecated APIs.

```bash
fext audit <file> [--json]
```

**Aliases:** `a`

### `risk`

Analyze permission risks and calculate a privacy score.

```bash
fext risk <file> [--json]
```

**Aliases:** `r`

### `scan`

Scan an extension for known vulnerable third-party libraries (e.g., jQuery, Lodash).

```bash
fext scan <file> [--json] [--csv]
```

### `analyze`

Perform deep analysis on extension code.

```bash
fext analyze <file> [options]
```

**Options:**

* `--complexity`: Calculate cyclomatic complexity of JavaScript files.
* `--entropy`: Calculate Shannon entropy to detect obfuscation/packing.
* `--domains`: Extract domains and URLs from source code.
* `--secrets`: Scan for potential secrets (API keys, tokens).
* `--yara <path>`: Scan against YARA rules (file or directory).
* `--json`: Output results as JSON.

### `report`

Generate a comprehensive report for an extension.

```bash
fext report <file> [options]
```

**Options:**

* `-o, --output <file>`: Output file path (default: `<filename>_REPORT.md`).
* `--json`: Output unified report as JSON.
* `--yara <path>`: Include YARA scan results in the report.

### `diff`

Compare two extension versions.

```bash
fext diff <old_file> <new_file> [--json]
```

### `verify`

Cryptographically verify a CRX3 file signature.

```bash
fext verify <file> [--json]
```

### `locales`

Inspect supported locales and message counts.

```bash
fext locales <file> [--json]
```

### `check`

Check for updates of local extension files against the Web Store.

```bash
fext check <file_or_dir> [--json]
```

### `serve`

Host the local repository as a Chrome/Edge Update Server.

```bash
fext serve [-d <directory>] [--host <host>] [-p <port>]
```

### `update-manifest`

Generate `update.xml` (Chrome/Edge) or `updates.json` (Firefox) for self-hosted extensions.

```bash
fext update-manifest <directory> --base-url <url> [--output <file>]
```

**Aliases:** `um`

### `mirror`

Synchronize a local directory with a list of extension IDs.

```bash
fext mirror <list_file> [-o <output_dir>] [--prune] [-w <workers>]
```

### `convert`

Convert extensions between formats.

```bash
fext convert <input> --to <format> [-o <output>]
```

**Supported Formats:** `zip`

### `optimize`

Losslessly compress images within an extension directory.

```bash
fext optimize <directory> [-q <quality>] [--json]
```

### `timeline`

Visualize the modification timeline of files within an extension.

```bash
fext timeline <file> [--json]
```

### `graph`

Generate a dependency graph of internal files.

```bash
fext graph <file> [-o <output.dot>]
```

### `stats`

Analyze a directory of extensions for aggregate statistics.

```bash
fext stats <directory> [--json]
```

### `explain`

Get a detailed explanation and risk assessment for a specific permission.

```bash
fext explain <permission> [--json]
```

### `plugin`

Manage Python-based plugins.

```bash
fext plugin <command> [args]
```

**Commands:**

* `list`: List installed plugins.
* `install <path>`: Install a plugin.
* `enable <name>`: Enable a plugin.
* `disable <name>`: Disable a plugin.
* `remove <name>`: Remove a plugin.

### `pack`

Pack an extension directory into a `.crx` file.

```bash
fext pack <directory> [options]
```

**Options:**

* `--pem <file>`: Path to private key file (generated if not exists).
* `--out <file>`: Output filename.

### `migrate`

Migrate a Manifest V2 extension to Manifest V3.

```bash
fext migrate <directory> [options]
```

**Options:**

* `--in-place`: Modify files in place.

### `ui`

Launch the terminal-based user interface (TUI).

```bash
fext ui
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
fext config [show|init]
```

### `schema`

Get JSON schema for various outputs.

```bash
fext schema <type>
```

**Types:** `config`, `audit`, `risk`, `history`, `scan`.

### `share`

Share a report file via a configured provider (e.g., GitHub Gist).

```bash
fext share <file> [--provider <provider>] [--description <text>]
```

**Options:**

* `--provider`: Sharing provider (default: `gist`).
* `--description`: Description for the shared file.

### `clean`

Clean up cache and temporary files.

```bash
fext clean [--cache] [--downloads] [--all] [--dry-run] [--force]
```

## Exit Codes

The CLI returns the following exit codes to indicate the status of the operation:

| Code | Name | Description |
| :--- | :--- | :--- |
| 0 | `SUCCESS` | Command completed successfully. |
| 1 | `ERROR` | Generic error (catch-all). |
| 2 | `USAGE` | Invalid arguments or usage error. |
| 3 | `NETWORK` | Network connection failed (DNS, timeout, connection refused). |
| 4 | `IO` | File system error (permission denied, disk full, file not found). |
| 5 | `CONFIG` | Configuration error (invalid config file, missing keys). |
| 6 | `NOT_FOUND` | Resource not found (extension ID, file). |
| 7 | `SECURITY` | Security check failed (signature verification, risk threshold). |
| 8 | `CANCELLED` | Operation cancelled by user (Ctrl+C). |
| 9 | `DEPENDENCY` | Missing external dependency. |
