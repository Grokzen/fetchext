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

### 🔍 Inspecting Extensions

You can inspect the metadata (manifest) of a downloaded extension file (`.crx` or `.xpi`) using the `inspect` command.

```bash
fext inspect <path_to_file>
```

**Example:**

```bash
fext inspect ublock-origin.crx
```

This will print details like Name, Version, Description, and Permissions. 📄

### 📦 Batch Downloading

You can download multiple extensions at once using a batch file.

```bash
fext batch <path_to_file> [-o <output_dir>]
```

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
fext batch my_extensions.txt -o downloads/
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
