# 📦 fetchext

A Python CLI tool to download browser extensions (Chrome, Edge, Firefox) directly from their web stores. 🚀

## �� Development and Agent Tooling

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
  rev: v2.0.0
  hooks:
    - id: fext-audit
    - id: fext-scan
```

## 🚀 Quick Start

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
```

**Edge:** 🌊

```bash
fext edge https://microsoftedge.microsoft.com/addons/detail/ublock-origin/odfafepnkmbhccpbejgmiehpchacaeak
```

**Firefox:** 🦊

```bash
fext firefox https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/
```

## 📚 Documentation

For full documentation, including advanced usage, analysis tools, and deployment guides, please visit our [Documentation Site](https://fetchext.grok.nu/).

* [CLI Reference](docs/cli.md)
* [Analysis & Forensics](docs/analysis.md)
* [Deployment & Enterprise](docs/deployment.md)
* [Installation](docs/installation.md)

### 🧠 AI Analysis

Enable AI-powered summaries in `~/.config/fext/config.toml`:

```toml
[ai]
enabled = true
api_key = "sk-..."
```

Then run:

```bash
fext analyze summary <file>
```

### 💅 Code Beautifier

Format minified JavaScript and JSON files:

```bash
fext beautify <file>
```

### 🔍 Similarity Search

Find similar extensions in a directory using fuzzy hashing:

```bash
fext similar <target_file> <directory>
```

### 🆚 Smart Diff

Compare two extension versions with whitespace ignoring and image analysis:

```bash
fext diff old.crx new.crx --ignore-whitespace
```

### 📦 Extension Packer

Pack a directory into a signed CRX3 file:

```bash
fext pack ./my-extension -o my-extension.crx
```

### � MV3 Migration

Automatically migrate Manifest V2 extensions to Manifest V3:

```bash
fext migrate ./my-extension
```

### �🖥️ TUI Dashboard

Launch the interactive dashboard to browse, download, and analyze extensions:

```bash
fext ui
```

## 💻 Development

### 🧹 Linting and Formatting

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
make lint
make format
```

### 🏗️ Building the Package

```bash
make build
```
