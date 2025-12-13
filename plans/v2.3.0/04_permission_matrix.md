# Plan: Permission Matrix

## Goal

Add `fext analyze permissions <directory>` to output a matrix showing permission usage across multiple extensions.

## Requirements

1. **CLI Command**: `fext analyze permissions <directory>`.
2. **Input**: A directory containing extension files (CRX, XPI, ZIP).
3. **Output**:
    * Console: Formatted table (Extensions x Permissions).
    * JSON: Structured data.
    * CSV: Spreadsheet-friendly format.
4. **Logic**:
    * Iterate through all extensions in the directory.
    * Extract permissions from each manifest.
    * Collect all unique permissions.
    * Build a matrix (List of Dicts or similar).

## Implementation Steps

### 1. Create `PermissionMatrixGenerator`

* File: `src/fetchext/analysis/permissions.py`
* Class `PermissionMatrixGenerator`
* Method `generate(directory: Path) -> Dict`
  * Returns:

      ```python
      {
          "permissions": ["tabs", "storage", ...], # Sorted list of all unique permissions
          "extensions": [
              {
                  "filename": "ext1.crx",
                  "permissions": ["tabs", "storage"]
              },
              ...
          ],
          "matrix": {
              "ext1.crx": {"tabs": True, "storage": True, ...}
          }
      }
      ```

### 2. Update `AuditCommand` (where `analyze` lives)

* Modify `src/fetchext/commands/audit.py`.
* Add `permissions` subcommand to `analyze` parser.
* Update `handle_analyze` to call `PermissionMatrixGenerator`.
* Implement output formatting (Table, JSON, CSV).

### 3. Testing

* Unit test for `PermissionMatrixGenerator`.
* Integration test for the CLI command.

## Verification

* Run `fext analyze permissions downloads/`.
* Verify output formats.
