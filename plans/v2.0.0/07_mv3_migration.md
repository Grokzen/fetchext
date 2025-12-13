# Plan: Manifest V3 Migration Assistant

## Goal

Add a `migrate` command to automatically convert Manifest V2 extensions to Manifest V3.

## Problem

Google Chrome is deprecating Manifest V2. Developers need tools to automate the tedious parts of the migration.

## Solution

Implement a `migrate` command that parses the manifest and source code, applying common transformations and generating a report of manual changes needed.

## Implementation Details

### 1. Core Logic (`src/fetchext/migration.py`)

- `MV3Migrator` class.
- `migrate(source_dir)`:
  - Read `manifest.json`.
  - **Manifest Transformations**:
    - Set `"manifest_version": 3`.
    - Move host permissions to `"host_permissions"`.
    - Rename `"browser_action"`/`"page_action"` to `"action"`.
    - Convert `"background": {"scripts": [...]}` to `"background": {"service_worker": "background.js", "type": "module"}`.
      - If multiple scripts, create a wrapper `background.js` that imports them? Or just warn.
    - Update `"content_security_policy"` format (string -> object).
    - Remove `"web_accessible_resources"` glob patterns (require objects).
  - **Code Analysis (Basic)**:
    - Scan JS files for `chrome.browserAction` -> `chrome.action`.
    - Scan for `chrome.webRequest` (warn about `declarativeNetRequest`).
    - Scan for `eval()` or `new Function()` (warn about CSP).

### 2. CLI Command (`src/fetchext/commands/migrate.py`)

- `fext migrate <directory> [--dry-run]`
- Outputs a migration report and optionally modifies files.

### 3. Dependencies

- `jsbeautifier` (to format modified JSON).

## Verification

- Create a dummy MV2 extension.
- Run `fext migrate`.
- Verify `manifest.json` is valid MV3.
- Verify warnings are generated for complex issues.
