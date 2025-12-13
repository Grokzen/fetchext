# Plan: Plugin System Enhancements

## Goal

Extend the plugin system to support new features (Packer, Migrator) and improve context passing.

## Problem

The current plugin system covers download and analysis, but not the new packing and migration features.

## Solution

Add new hooks:

- `pre_pack`: Called before packing starts. Can modify source directory or cancel.
- `post_pack`: Called after packing. Can access the output CRX.
- `pre_migrate`: Called before migration.
- `post_migrate`: Called after migration. Can access the report.

## Implementation Details

### 1. Update `HookManager` (`src/fetchext/hooks.py`)

- Ensure `HookContext` is flexible enough to carry new data types (e.g., `MigrationReport`).

### 2. Integrate Hooks

- **Packer**:
  - `pre_pack(ctx)`: `ctx.source_dir`, `ctx.output_path`.
  - `post_pack(ctx)`: `ctx.output_path`.
- **Migrator**:
  - `pre_migrate(ctx)`: `ctx.source_dir`.
  - `post_migrate(ctx)`: `ctx.report`.

### 3. Verification

- Create a test plugin that logs these events.
- Run `pack` and `migrate` commands.
- Verify logs.
