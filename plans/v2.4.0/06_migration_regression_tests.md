# Plan: Migration Regression Tests

## Goal

Implement a suite of "golden" tests for the `fext migrate` command to ensure that Manifest V2 to Manifest V3 conversions are accurate and stable over time.

## Motivation

The migration logic involves complex transformations (manifest structure, permissions, background scripts, CSP). As we enhance the migration tool, we need to ensure we don't break existing valid conversions. Golden tests (snapshot testing) provide a safety net.

## Implementation Steps

### 1. Create Test Data Directory

- Create `tests/data/migration/cases/`.
- Create subdirectories for different scenarios (e.g., `basic`, `background_scripts`, `csp`, `permissions`).

### 2. Create Golden Data

- For each scenario, create:
  - `input/manifest.json`: The MV2 manifest.
  - `expected/manifest.json`: The expected MV3 manifest.
  - `input/background.js` (optional): If background script changes are tested.
  - `expected/service_worker.js` (optional): Expected service worker content.

### 3. Create Test Suite

- Create `tests/unit/test_migration_golden.py`.
- Use `pytest` to iterate over cases in `tests/data/migration/cases/`.
- For each case:
  - Copy `input` to a temp directory.
  - Run `Migrator.migrate()`.
  - Compare generated files with `expected` files.

## Testing Strategy

- **Data-Driven**: The test runner should automatically pick up new cases added to the data directory.
- **Exact Match**: JSON comparisons should be exact (ignoring whitespace/ordering if possible, or canonicalized).

## Documentation

- Update `CHANGELOG.md`.
