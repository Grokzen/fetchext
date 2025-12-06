# Project Context & AI Instructions

This file documents the project's history, architectural decisions, and coding standards. It is intended to provide context for AI assistants (like GitHub Copilot) to ensure consistency and awareness of previous work.

## Project Overview

**Name**: `fetchext` (formerly `chrome-extension-downloader`)
**CLI Command**: `fext`
**Purpose**: A Python CLI tool to download browser extensions (Chrome, Edge, Firefox) directly from their respective web stores.

## Tech Stack & Requirements

- **Language**: Python 3.11+
- **Build System**: `setuptools` (configured via `pyproject.toml`)
- **Dependencies**: `requests`, `rich`, `cryptography`, `textual`, `lizard`, `tomli-w`, `Pillow` (minimal dependencies preferred)
- **Optional Dependencies**: `yara-python` (for security scanning)
- **Linting/Formatting**: `ruff`
- **Task Management**: `Makefile`
- **Type Hints**: **FORBIDDEN**. Do not use Python type hints (e.g., `def foo(x: int) -> str:`). Keep code dynamic and clean.

## Architectural Decisions & Patterns

### 1. Modern Path Handling

- **Decision**: Use `pathlib.Path` exclusively instead of `os.path`.
- **Reasoning**: Provides an object-oriented interface for filesystem paths, making code more readable and robust.

### 2. Project Structure (`src` layout)

- **Decision**: Use the `src/` layout pattern.
- **Structure**:

  ```text
  src/
    fetchext/
      analysis/
        __init__.py
        complexity.py
        domains.py
        entropy.py
        explainer.py
        graph.py
        locales.py
        yara.py
      downloaders/
        __init__.py
        base.py
        chrome.py
        edge.py
        firefox.py
      __init__.py
      auditor.py
      batch.py
      cli.py
      config.py
      console.py
      core.py
      crx.py
      diff.py
      history.py
      hooks.py
      inspector.py
      mirror.py
      network.py
      optimizer.py
      plugins.py
      preview.py
      protobuf.py
      risk.py
      scanner.py
      schemas.py
      secrets.py
      server.py
      setup.py
      tui.py
      tutorial.py
      utils.py
      verifier.py
  pyproject.toml
  Makefile
  ```

- **Reasoning**: Prevents import errors during testing and separates concerns by browser type.

### 3. Extensibility (Strategy Pattern)

- **Decision**: Use a `BaseDownloader` abstract base class.
- **Reasoning**: Allows easy addition of new browsers (e.g., Edge, Firefox) by implementing a new class that inherits from `BaseDownloader` and registering it in the CLI dispatch logic.

### 4. Configuration Management

- **Decision**: Removed `python-dotenv` and `.env` files.
- **Reasoning**: The tool is currently a stateless CLI that accepts arguments. It does not require persistent configuration or secrets at this stage.

### 5. Error Handling

- **Strategy**: Fail fast and clean up.
- **Implementation**: If a download results in an empty file (0 bytes) or fails, the script must clean up (delete) the partial/empty file and exit with a non-zero status code.
- **Logging**: Use standard `logging` library. Format is simplified to `%(levelname)s: %(message)s`.

### 6. Testing Strategy

- **Framework**: `pytest` with `pytest-mock`, `pytest-cov`, and `pyfakefs`.
- **Structure**: 4-Level Testing Strategy.
    1. **Unit**: Logic isolation (e.g., ID extraction). Fast, no I/O.
    2. **CLI**: Argument parsing and help output.
    3. **Integration**: Mocked network requests and file system (using `pyfakefs`). Verifies file handling and flow without internet or real disk usage.
    4. **Live**: Real E2E tests against Web Stores. Marked with `@pytest.mark.live`.
- **Execution**: `make test` (Levels 1-3), `make test-live` (Level 4).

### 7. CRX Parsing

- **Decision**: Use `CrxDecoder` and `PartialFileReader` for robust CRX3 parsing.
- **Reasoning**: Avoids loading entire files into memory and searching for ZIP signatures, which is inefficient and error-prone. Supports streaming-like access to the embedded ZIP archive.

### 8. Network Resilience

- **Decision**: Use `requests.adapters.HTTPAdapter` with `urllib3.util.retry.Retry` for all network requests.
- **Reasoning**: Provides automatic retries with backoff for transient failures (5xx, connection errors) without adding external dependencies like `tenacity`.

### 9. Library Mode Architecture

- **Decision**: Decouple CLI logic from core functionality.
- **Structure**:
  - `src/fetchext/core.py`: Contains high-level functions (`download_extension`, `search_extension`, etc.) that can be imported and used by other Python scripts.
  - `src/fetchext/cli.py`: Handles argument parsing, logging setup, and calls `core` functions.
  - `src/fetchext/__init__.py`: Exports the public API.
- **Reasoning**: Allows `fetchext` to be used as a library in other projects, not just as a CLI tool.

### 11. Analysis Module

- **Decision**: Group specialized analysis logic in `src/fetchext/analysis/`.
- **Reasoning**: Keeps the root package clean and organizes complex analysis features (complexity, entropy, domains, graphs) into their own modules.

### 12. TUI Integration

- **Decision**: Use `textual` for interactive interfaces (`ui`, `tutorial`).
- **Reasoning**: Provides a rich, terminal-based UI experience that is distinct from the standard CLI output, suitable for browsing and learning.

### 13. Image Optimization

- **Decision**: Use `Pillow` for image processing.
- **Reasoning**: Standard library for Python image manipulation, robust and widely supported, enabling lossless compression features.

## Development Workflow

- **Setup**: `make setup` (creates venv, installs package in editable mode `pip install -e .`).
- **Run**: `fext download <browser> <url> [--save-metadata] [--extract]` or `fext search firefox <query>`.
- **Extract**: `fext extract <file> [-o <output_dir>]`.
- **Build**: `make build` (uses `build` module to generate wheels/sdist).
- **Lint**: `make lint` / `make format`.
- **Test**: `make test` (Unit/CLI/Integration) and `make test-live` (E2E).
- **CI**: `make ci` (runs lint, build, and tests).

## CI/CD

- **Platform**: GitHub Actions
- **Workflow**: `.github/workflows/ci.yml`
- **Matrix**: Python 3.11, 3.12, 3.13
- **Steps**: Lint (ruff), Build, Test (pytest).

## History & Evolution

1. **Inception**: Started as a single script `main.py`.
2. **Refactor**: Moved to `src/fetchext/cli.py` to support packaging.
3. **Renaming**: Renamed from `chrome-extension-downloader` to `fetchext` (`fext`).
4. **Multi-Browser Support**: Refactored to support Chrome, Edge, and Firefox using a modular downloader architecture.
5. **CI/CD Integration**: Added GitHub Actions workflow and Makefile targets for automated testing and validation.
6. **Testing Overhaul**: Implemented comprehensive 4-level testing strategy (Unit, CLI, Integration, Live) using `pytest`.
7. **Advanced Analysis**: Added deep inspection tools (complexity, entropy, domains, YARA) and forensic capabilities (timeline, graph).
8. **Local Serving**: Added capabilities to host and mirror extensions locally (`serve`, `mirror`, `update-manifest`).
9. **User Experience**: Enhanced UX with TUI (`ui`), interactive tutorial (`tutorial`), and rich CLI output.

## Future Considerations

- **Publishing**: The project is configured for PyPI publishing.
- **Version Support**: Strictly targeting Python 3.11+.

## Development and Agent Tooling

This repository is an experiment in **100% Vibe Coding** - all code is generated, maintained, and evolved exclusively through Agent tooling. No manual coding is permitted.

### Experimental Setup

- **IDE**: VSCode Insider program (required for Agent integration)
- **AI Model**: Gemini 2.0 Flash or Grok 3 Beta (exclusively)
- **Approach**: Zero manual intervention - all development is Agent-driven

### 100% Vibe Coding Policy

This project serves as a proof-of-concept for fully automated software development:

- **No Manual Code**: All code changes must be produced by the Agent.
- **Rejection Criteria**: Manual submissions or changes from other AI models will be rejected.
- **Quality Control**: The Agent maintains consistent coding standards and patterns.
- **Evolution**: The codebase grows and adapts through iterative Agent interactions.

## Agent Protocols

### 1. Documentation Self-Maintenance

- **Rule**: This file (`.github/copilot-instructions.md`) is the source of truth for project context.
- **Action**: If a new architectural decision, coding standard, or workflow pattern emerges during a chat session, the Agent **MUST** update this file to reflect the change.
- **Goal**: Ensure future context windows have access to the latest project state and rules.

### 2. Git Usage Policy

- **Rule**: **NO AUTOMATIC COMMITS**.
- **Action**: The Agent shall never run `git commit` without an explicit instruction from the user.
- **Pre-Commit Protocol**:
    1. **Lint Python**: Run `ruff check .`.
    2. **Fix Python**: If errors exist, run `ruff check . --fix`.
    3. **Lint Markdown**: Run `npx markdownlint-cli@0.31.1 "**/*.md"`.
    4. **Fix Markdown**: If errors exist, run `npx markdownlint-cli@0.31.1 "**/*.md" --fix`.
    5. **Block**: If unfixable errors remain in either, **ABORT** the commit and report issues to the user.
- **Workflow**:
    1. Perform necessary code changes.
    2. Verify changes (lint, test).
    3. Wait for user to request a commit.
    4. When requested, execute the **Pre-Commit Protocol** before committing.
    5. Write a clear, descriptive commit message following the project's history style.

### 3. Changelog Maintenance

- **Rule**: **ALWAYS UPDATE CHANGELOG.md**.
- **When**: Whenever a new feature, bug fix, or significant change is implemented.
- **Versioning Policy**:
  - **Default**: Add changes to the **current minor version** (e.g., if on 0.2.0, keep adding to 0.2.0).
  - **Bump**: Only increment the version number (e.g., to 0.3.0) when explicitly instructed by the user.
- **Format**: Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
- **Structure**:
  - Group changes under the current version header.
  - Use subsections: `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`.
- **Action**:
    1. Check `CHANGELOG.md` for the current state.
    2. Add a concise, bulleted entry describing the change under the current version.
    3. If (and only if) instructed to release a new version, update `pyproject.toml` version as well.
    4. Ensure `CHANGELOG.md` passes markdown linting (no duplicate headers within the same section, correct spacing).

### 4. README Consistency Protocol

- **Rule**: Documentation must never lag behind code.
- **Trigger**: Any modification to `cli.py`, addition of flags, or change in user-facing behavior.
- **Action**:
    1. Update `README.md` immediately after implementing the feature.
    2. Ensure usage examples are copy-pasteable and correct.
    3. Verify that `fext --help` output aligns with documented commands.

### 5. Feature Blacklist Protocol

- **Rule**: **NEVER IMPLEMENT BLACKLISTED FEATURES**.
- **Source**: `.github/feature-blacklist.md`.
- **Action**:
    1. Before suggesting a new feature or adding an item to `ROADMAP.md`, check `.github/feature-blacklist.md`.
    2. If the feature (or a close variant) is listed there, **DO NOT** suggest it.
    3. If the user asks for a blacklisted feature, politely decline and reference the blacklist reasoning.

