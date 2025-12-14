# Plan: TUI Themes

## Goal

Add support for user-configurable color schemes (themes) in `config.toml` for the TUI.

## Objectives

1. Define a theme schema in `config.toml`.
2. Update `src/fetchext/tui.py` (or wherever the TUI app is defined) to load these colors.
3. Apply colors to Textual widgets using CSS variables or dynamic CSS.

## Implementation Details

### 1. Config Schema

Add a `[tui.theme]` section to `config.toml`.

```toml
[tui.theme]
primary = "#00ff00"
secondary = "#ff00ff"
background = "#000000"
surface = "#111111"
error = "#ff0000"
```

### 2. TUI Update

* In `FetchextApp.on_mount` or `__init__`, load the config.
* Textual allows setting design tokens.
* We can generate CSS dynamically or use `self.design` (if available in newer Textual versions) or just inject CSS variables.
* Textual uses CSS variables like `$primary`, `$secondary`, etc. We can override these.

### 3. Theme Manager

* Create `src/fetchext/ui/theme.py` to handle loading and applying themes.
* It should support a default theme and user overrides.

## Risks

* Textual's theming system might have changed (it evolves fast). We need to check how to override standard colors.
* CSS injection is the safest bet.

## Verification

* Add a test case that loads a custom config and verifies the app's CSS variables.
