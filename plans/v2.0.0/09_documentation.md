# Plan: Documentation Update

## Goal
Create comprehensive documentation for the new v2.0.0 features.

## Problem
New features (TUI Dashboard, Packer, Migrator) are only briefly mentioned in README. Users need detailed guides.

## Solution
Create new documentation pages and update existing ones.

## Implementation Details

### 1. New Pages
-   `docs/tui.md`:
    -   Dashboard overview.
    -   Browser selection.
    -   Search and download workflow.
    -   Keyboard shortcuts.
-   `docs/packer.md`:
    -   Usage of `fext pack`.
    -   Key generation and management.
    -   CRX3 format explanation.
-   `docs/migration.md`:
    -   Usage of `fext migrate`.
    -   What it does (manifest changes, file changes).
    -   Manual steps required after migration.

### 2. Update Existing Pages
-   `docs/cli.md`: Add `pack`, `migrate`, `ui` (update), `diff` (update), `similar` (update).

## Verification
-   Build docs using `mkdocs build` (if available) or just verify markdown rendering.
