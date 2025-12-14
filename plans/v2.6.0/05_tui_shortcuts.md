# Plan: TUI Keyboard Shortcuts

## Goal

Add configurable keyboard shortcuts to the TUI to improve power user efficiency.

## Requirements

1. Support default shortcuts for common actions:
    * `/`: Focus search input.
    * `Ctrl+d`: Download selected extension.
    * `Ctrl+q`: Quit.
    * `j` / `k`: Navigate list (if not already supported by Textual).
    * `Enter`: View details / Download.
2. Allow users to configure shortcuts in `config.toml`.
3. Display shortcuts in the UI (e.g., in the footer).

## Implementation Details

### 1. Configuration

Update `src/fetchext/schemas.py` to include a `[tui.keybindings]` section.

```toml
[tui.keybindings]
focus_search = "/"
download = "ctrl+d"
quit = "ctrl+q"
```

### 2. TUI Update (`src/fetchext/tui.py`)

* Load keybindings from config.
* Bind keys in the `FetchextApp` class.
* Update the `Footer` to reflect custom bindings.

### 3. Documentation

* Update `docs/configuration.md`.
* Update `README.md`.

## Verification

* Unit tests for configuration loading.
* Manual verification (or E2E test if possible) of keybindings.
