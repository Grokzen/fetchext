# TUI Dashboard

Fetchext v2.0.0 introduces a rich Terminal User Interface (TUI) for a more interactive experience.

## Overview

The TUI Dashboard provides a visual way to:

- View repository statistics (downloaded extensions, total size).
- Browse download history.
- Search for extensions across multiple browsers (Chrome, Edge, Firefox).
- Download extensions directly from the interface.

## Launching the Dashboard

To start the TUI, run:

```bash
fext ui
```

## Interface Sections

### 1. Dashboard Tab

The main landing page showing:

- **Stats**: Total extensions downloaded, total disk usage.
- **Recent Activity**: A log of recent downloads and actions.
- **System Info**: Current Python version and OS details.

### 2. Browser Tabs (Chrome, Edge, Firefox)

Each browser has its own tab where you can:

- **Search**: Enter a query in the search bar to find extensions.
- **Results**: View search results in a data table.
- **Download**: Select an extension and press `d` to download it.

## Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| `q` | Quit the application |
| `d` | Toggle Dark/Light mode |
| `Ctrl+p` | Open Command Palette (if available) |

## Navigation

- Use your mouse to click tabs and buttons.
- Use `Tab` and `Shift+Tab` to navigate between focusable elements.
- Use `Enter` to activate buttons or inputs.
