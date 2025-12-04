# Project Context & AI Instructions

This file documents the project's history, architectural decisions, and coding standards. It is intended to provide context for AI assistants (like GitHub Copilot) to ensure consistency and awareness of previous work.

## Project Overview
**Name**: `fetchext` (formerly `chrome-extension-downloader`)
**CLI Command**: `fext`
**Purpose**: A Python CLI tool to download browser extensions (Chrome, Edge, Firefox) directly from their respective web stores.

## Tech Stack & Requirements
- **Language**: Python 3.11+
- **Build System**: `setuptools` (configured via `pyproject.toml`)
- **Dependencies**: `requests` (minimal dependencies preferred)
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
  ```
  src/
    fetchext/
      downloaders/
        __init__.py
        base.py
        chrome.py
        edge.py
        firefox.py
      __init__.py
      cli.py
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

## Development Workflow
- **Setup**: `make setup` (creates venv, installs package in editable mode `pip install -e .`).
- **Run**: `fext download <browser> <url>` or `fext search firefox <query>`.
- **Build**: `make build` (uses `build` module to generate wheels/sdist).
- **Lint**: `make lint` / `make format`.
- **Test**: `make test-downloads` (runs live download tests for all supported browsers).
- **CI**: `make ci` (runs lint, build, and test-downloads).

## CI/CD
- **Platform**: GitHub Actions
- **Workflow**: `.github/workflows/ci.yml`
- **Matrix**: Python 3.11, 3.12, 3.13
- **Steps**: Lint (ruff), Build, Test Downloads (live integration test).

## History & Evolution
1.  **Inception**: Started as a single script `main.py`.
2.  **Refactor**: Moved to `src/fetchext/cli.py` to support packaging.
3.  **Renaming**: Renamed from `chrome-extension-downloader` to `fetchext` (`fext`).
4.  **Multi-Browser Support**: Refactored to support Chrome, Edge, and Firefox using a modular downloader architecture.
5.  **CI/CD Integration**: Added GitHub Actions workflow and Makefile targets for automated testing and validation.

## Future Considerations
- **Testing**: No unit tests exist yet. Future work should add `pytest`.
- **Publishing**: The project is configured for PyPI publishing.
- **Version Support**: Strictly targeting Python 3.11+.

## Development and Agent Tooling

This repository is an experiment in **100% Vibe Coding** - all code is generated, maintained, and evolved exclusively through Agent tooling. No manual coding is permitted.

### Experimental Setup

*   **IDE**: VSCode Insider program (required for Agent integration)
*   **AI Model**: Gemini 2.0 Flash or Grok 3 Beta (exclusively)
*   **Approach**: Zero manual intervention - all development is Agent-driven

### 100% Vibe Coding Policy

This project serves as a proof-of-concept for fully automated software development:

*   **No Manual Code**: All code changes must be produced by the Agent.
*   **Rejection Criteria**: Manual submissions or changes from other AI models will be rejected.
*   **Quality Control**: The Agent maintains consistent coding standards and patterns.
*   **Evolution**: The codebase grows and adapts through iterative Agent interactions.

## Agent Protocols

### 1. Documentation Self-Maintenance
- **Rule**: This file (`.github/copilot-instructions.md`) is the source of truth for project context.
- **Action**: If a new architectural decision, coding standard, or workflow pattern emerges during a chat session, the Agent **MUST** update this file to reflect the change.
- **Goal**: Ensure future context windows have access to the latest project state and rules.

### 2. Git Usage Policy
- **Rule**: **NO AUTOMATIC COMMITS**.
- **Action**: The Agent shall never run `git commit` without an explicit instruction from the user.
- **Pre-Commit Protocol**:
    1.  **Lint**: Run `ruff check .` before generating the commit command.
    2.  **Fix**: If errors exist, run `ruff check . --fix`.
    3.  **Block**: If unfixable errors remain, **ABORT** the commit and report issues to the user.
- **Workflow**:
    1.  Perform necessary code changes.
    2.  Verify changes (lint, test).
    3.  Wait for user to request a commit.
    4.  When requested, execute the **Pre-Commit Protocol** before committing.
    5.  Write a clear, descriptive commit message following the project's history style.
