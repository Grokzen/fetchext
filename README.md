# 📦 fetchext

A Python CLI tool to download browser extensions (Chrome, Edge, Firefox) directly from their web stores. 🚀

## 🤖 Development and Agent Tooling

This repository is an experiment in **100% Vibe Coding** - all code is generated, maintained, and evolved exclusively through Agent tooling. No manual coding is permitted. ✨

### 🧪 Experimental Setup

* **IDE**: VSCode Insider program (required for Agent integration) 💻
* **AI Model**: Gemini 2.0 Flash or Grok 3 Beta (exclusively) 🧠
* **Approach**: Zero manual intervention - all development is Agent-driven ⚡

### 📜 100% Vibe Coding Policy

This project serves as a proof-of-concept for fully automated software development:

* **No Manual Code**: All code changes must be produced by the Agent. 🚫✋
* **Rejection Criteria**: Manual submissions or changes from other AI models will be rejected. ❌
* **Quality Control**: The Agent maintains consistent coding standards and patterns. ✅
* **Evolution**: The codebase grows and adapts through iterative Agent interactions. 🌱

### 📝 Submission Guidelines

To participate in this experiment:

* Use only VSCode Insider with Gemini 2.0 Flash or Grok 3 Beta for any interactions.
* Allow the Agent to handle all code modifications.
* Manual pull requests will be declined to preserve the purity of the experiment.
* Report issues or request features through Agent-mediated channels. 🗣️

This repository demonstrates the potential of fully automated development workflows while maintaining high code quality and consistency.

## 📋 Requirements

* Python 3.11 or higher 🐍

## 🛠️ Setup

1. **Create a virtual environment and install the package:**

    ```bash
    make setup
    ```

### 🐳 Docker

You can run `fetchext` using Docker:

```bash
docker run --rm -v $(pwd):/app/downloads ghcr.io/grok/fetchext download chrome <url> -o /app/downloads
```

### 🪝 Pre-commit Hook

You can use `fetchext` in your [pre-commit](https://pre-commit.com) config:

```yaml
- repo: https://github.com/grok/fetchext
  rev: v0.7.0
  hooks:
    - id: fext-audit
    - id: fext-scan
```

## 🚀 Usage

The CLI requires two arguments: the browser type and the extension URL.

```bash
fext <browser> <url>
```

* **browser**: `chrome` (or `c`), `edge` (or `e`), `firefox` (or `f`) 🌐
* **url**: The URL of the extension in the respective web store. 🔗

### 💡 Examples

**Chrome:** 🌈

```bash
fext chrome https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh
# or
fext c https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh
```

**Edge:** 🌊

```bash
fext edge https://microsoftedge.microsoft.com/addons/detail/ublock-origin/odfafepnkmbhccpbejgmiehpchacaeak
```

**Firefox:** 🦊

```bash
fext firefox https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/
```

The extension will be downloaded to the current directory. 📥

### ⚙️ Advanced Options

**Save Metadata:** 📝

Save extension details (ID, name, version, source, timestamp) to a JSON file alongside the extension.

```bash
fext download chrome <url> --save-metadata
# or
fext download chrome <url> -m
```

**Auto-Extract:** 📂

Automatically unzip the downloaded extension into a folder.

```bash
fext download chrome <url> --extract
# or
fext download chrome <url> -x
```

### � Searching Extensions

You can search for extensions directly from the CLI (currently supports Firefox).

```bash
fext search firefox <query>
```

**Example Output:**

```bash
$ fext search firefox ublock

[15:59:23] INFO     Starting fetchext...
                                                                  Search Results for 'ublock'
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                   ┃ Slug                ┃ GUID                                   ┃ URL                                                                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ uBlock Origin          │ ublock-origin       │ uBlock0@raymondhill.net                │ https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/       │
│ Block Site             │ block-website       │ {54e2eb33-18eb-46ad-a4e4-1329c29f6e17} │ https://addons.mozilla.org/en-US/firefox/addon/block-website/       │
│ AdGuard AdBlocker      │ adguard-adblocker   │ adguardadblocker@adguard.com           │ https://addons.mozilla.org/en-US/firefox/addon/adguard-adblocker/   │
│ LeechBlock NG          │ leechblock-ng       │ leechblockng@proginosko.com            │ https://addons.mozilla.org/en-US/firefox/addon/leechblock-ng/       │
│ AdBlocker for YouTube™ │ adblock-for-youtube │ jid1-q4sG8pYhq8KGHs@jetpack            │ https://addons.mozilla.org/en-US/firefox/addon/adblock-for-youtube/ │
└────────────────────────┴─────────────────────┴────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────┘
[15:59:24] INFO     Script finished successfully.
```

### �🔍 Inspecting Extensions

You can inspect the metadata (manifest) of a downloaded extension file (`.crx` or `.xpi`) using the `inspect` command.

```bash
fext inspect <path_to_file>
```

**Example:**

```bash
fext inspect ublock-origin.crx
```

This will print details like Name, Version, Description, and Permissions. 📄

### � Extracting Extensions

You can extract an existing extension file (`.crx` or `.xpi`) using the `extract` command.

```bash
fext extract <path_to_file> [-o <output_dir>]
```

**Example:**

```bash
fext extract ublock-origin.crx
```

This will extract the contents into a folder named `ublock-origin` in the current directory.

### �📦 Batch Downloading

You can download multiple extensions at once using a batch file.

```bash
fext batch <path_to_file> [-o <output_dir>] [-w <workers>]
```

**Arguments:**

* `-o`, `--output`: Directory to save downloaded files (default: current directory).
* `-w`, `--workers`: Number of parallel downloads (default: 4).

**Batch File Format:**

The batch file should contain one entry per line in the format: `<browser> <url_or_id>`. Lines starting with `#` are ignored.

```text
# My Extensions
chrome aicmkgpgakddgnaphhhpliifpcfhicfo
edge nbjbemmokmdpdokpnbfpdfbikmhgilmc
firefox https://addons.mozilla.org/en-US/firefox/addon/postman_interceptor/
```

**Example:**

```bash
fext batch my_extensions.txt -o downloads/ -w 8
```

### 🔄 Local Update Server

Generate an update manifest (`update.xml` or `updates.json`) for a directory of downloaded extensions. This allows you to host your own extension updates.

```bash
fext update-manifest <directory> --base-url <url>
```

**Example:**

```bash
fext update-manifest ./downloads --base-url http://localhost:8000/extensions
```

This will generate `update.xml` (for Chrome/Edge) and/or `updates.json` (for Firefox) in the `./downloads` directory.

### 🪞 Mirror Mode

Synchronize a local directory with a list of extensions. This command will download missing extensions, update existing ones, and optionally remove files not in the list.

```bash
fext mirror <list_file> [--output-dir <dir>] [--prune]
```

**Arguments:**

* `--prune`: Remove files in the output directory that are not in the list.
* `--workers`: Number of parallel downloads.

**Example:**

```bash
fext mirror my_extensions.txt -o ./mirror --prune
```

### 🛡️ Dependency Scanner

Scan an extension file for known vulnerable third-party libraries (e.g., jQuery, Lodash).

```bash
fext scan <file> [--json]
```

**Example:**

```bash
fext scan ublock-origin.crx
```

This will list detected libraries and flag any with known vulnerabilities.

### 📊 Markdown Reports

Generate a comprehensive Markdown report for an extension, including metadata, risk analysis, and file structure.

```bash
fext report <file> [-o <output_file>]
```

**Example:**

```bash
fext report ublock-origin.crx
```

This will generate `ublock-origin_REPORT.md` in the current directory.

### ⚙️ Configuration Wizard

Interactively set up or update your configuration file (`~/.config/fext/config.toml`).

```bash
fext setup
```

This wizard will guide you through setting default download directory, worker count, and other preferences.

### 🔄 Format Converter

Convert extensions between formats (e.g., CRX to ZIP, Directory to ZIP).

```bash
fext convert <input> --to zip [-o <output>]
```

**Example:**

```bash
fext convert ublock-origin.crx --to zip
```

This will create `ublock-origin.zip` (stripping the CRX header).

### 📊 Repository Statistics

Analyze a local directory of extensions to get insights like total size, MV2/MV3 breakdown, and permission usage.

```bash
fext stats <directory>
```

### 🧠 Permission Explainer

Get a detailed explanation and risk assessment for a specific permission.

```bash
fext explain <permission>
```

**Example:**

```bash
fext explain tabs
```

### 🎲 Entropy Analysis

Analyze the entropy of files within an extension to detect potential obfuscation, packing, or encrypted data.

```bash
fext analyze --entropy <file>
```

**Example:**

```bash
fext analyze --entropy ublock-origin.crx
```

### 📄 Documentation & Completion

**Man Page:**

Generate a standard man page for `fext`.

```bash
make docs
man -l docs/man/fext.1
```

**Shell Completion:**

Generate shell completion scripts for Bash and Zsh.

```bash
make docs
source docs/completions/fext.bash  # For Bash
source docs/completions/fext.zsh   # For Zsh
```

## 💻 Development

### 🧹 Linting and Formatting

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

To run the linter:

```bash
make lint
```

To format the code:

```bash
make format
```

### 🏗️ Building the Package

To build the package for distribution (creates `dist/` directory with wheel and sdist):

```bash
make build
```

### ⚙️ Makefile

A `Makefile` is provided for convenience:

* `make setup`: Create virtual environment and install dependencies (including build tools).
* `make run`: Run the script.
* `make lint`: Run linting checks.
* `make format`: Format the code.
* `make build`: Build the package.
* `make clean`: Remove temporary files, virtual environment, and build artifacts. 🗑️
