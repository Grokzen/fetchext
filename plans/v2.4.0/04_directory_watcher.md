# Plan: Directory Watcher

## Goal

Add `fext watch <dir>` to monitor a folder for new `.crx` or `.xpi` files and automatically trigger analysis workflows (scan, report, extract) as they arrive.

## Motivation

Security analysts often have a "drop folder" where they dump suspicious extensions. Automating the analysis pipeline upon file arrival saves time and ensures consistent processing.

## Implementation Steps

### 1. Create `src/fetchext/commands/watch.py`

- Implement the `watch` command.
- Use `watchdog` library for file system monitoring.
- Support configuration for actions (e.g., `--extract`, `--report`, `--scan`).

### 2. Create `src/fetchext/watcher.py`

- Implement `ExtensionEventHandler` inheriting from `watchdog.events.FileSystemEventHandler`.
- Handle `on_created` events.
- Filter for `.crx`, `.xpi`, `.zip`.
- Execute configured actions.

### 3. Update `pyproject.toml`

- Add `watchdog` dependency.

### 4. Register Command

- Update `src/fetchext/cli.py`.

## Testing Strategy

- **Unit Test**: Mock `watchdog` observer and handler.
- **Integration Test**: Simulate file creation and verify actions.

## Documentation

- Update `docs/cli.md`.
