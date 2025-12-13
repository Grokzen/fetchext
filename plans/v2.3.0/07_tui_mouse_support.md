# Plan: TUI Mouse Support

## Goal

Enable mouse interaction in the `fext ui` Terminal User Interface. Users should be able to click on tabs to switch views, click on table rows to select extensions, and click buttons to trigger actions (download, search).

## Objectives

1. Verify current mouse support status in `textual`. (It is usually enabled by default, but might need specific widget handling).
2. Enhance `DataTable` in `src/fetchext/tui.py` to handle click events (`on_data_table_row_selected` is already there, but maybe `on_click` needs handling for specific cells?).
3. Ensure `Tabs` are clickable (Textual `Tabs` are clickable by default).
4. Add explicit "Download" buttons or context menus if row clicking isn't intuitive enough.
5. Test with mouse in a terminal that supports it.

## Implementation Details

### 1. `src/fetchext/tui.py`

- The `DataTable` widget supports `cursor_type="row"`.
- We need to ensure `on_data_table_row_selected` is correctly wired up.
- Textual apps usually handle mouse events automatically if the terminal supports it.
- We might need to add `BINDINGS` for mouse actions if we want custom behavior.

### 2. UX Improvements

- Add a `Footer` with clickable keys? (Textual `Footer` items are clickable).
- Maybe add a "Download" button in the details pane that can be clicked.

### 3. Verification

- Since I cannot physically click, I will verify that the code uses standard Textual widgets and event handlers that support mouse interaction.
- I will add a test case that simulates a click event if possible (using `pilot.click`).

## Steps

1. Review `src/fetchext/tui.py`.
2. Add a "Download" button to the details panel (currently it might just be keybindings).
3. Ensure `DataTable` selection works with mouse.

## Verification

- Use `textual`'s `Pilot` to simulate clicks in tests.
