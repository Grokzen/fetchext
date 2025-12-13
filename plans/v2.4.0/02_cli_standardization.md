# Plan: CLI Output Standardization

## Goal

Create a central `Theme` class to enforce consistent colors, emojis, and formatting across all CLI commands. This improves the professional look and feel of the tool and makes it easier to change styles globally.

## Motivation

Currently, colors and emojis are hardcoded in various commands (e.g., `[green]`, `[red]`, `✅`, `❌`). This leads to inconsistencies and makes it difficult to maintain a cohesive visual identity.

## Implementation Steps

### 1. Create `src/fetchext/theme.py`

- Define a `Theme` class using `rich` styles.
- Define constants for common status indicators (SUCCESS, ERROR, WARNING, INFO).
- Define standard colors for different types of data (e.g., IDs, versions, paths).

### 2. Refactor `src/fetchext/console.py`

- Update the `Console` wrapper to use the new `Theme` class.
- Provide helper methods for printing standardized messages (e.g., `print_success`, `print_error`).

### 3. Update Commands

- Refactor existing commands to use the new `Theme` and `Console` methods instead of hardcoded strings.
- Focus on high-visibility commands first: `download`, `inspect`, `search`.

## Testing Strategy

- **Unit Test**: Verify that `Theme` returns expected styles.
- **Visual Verification**: Run commands to ensure output looks correct (manual verification or snapshot testing if available).

## Documentation

- Update `docs/cli.md` (if applicable) to mention the new theming capability.
