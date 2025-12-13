# TUI Dashboard Implementation Plan

## Goal

Add a "Home" screen to the `fext ui` TUI that displays repository statistics and insights.

## Problem

Currently, `fext ui` starts directly in the search/browser view. Users don't have an overview of their local repository state (how many extensions, disk usage, risk profile).

## Solution

Implement a Dashboard screen as the default view when opening `fext ui`.
It should show:

1. **Summary Stats**: Total extensions, total size, MV2 vs MV3 count.
2. **Risk Distribution**: A breakdown of extensions by risk level (Critical, High, Medium, Low, Safe).
3. **Recent Activity**: List of recently downloaded/extracted extensions (from History).

## Implementation Details

### 1. Dependencies

- `textual` (already included).
- `rich` (already included) for bar charts/tables.

### 2. Core Logic (`src/fetchext/tui.py`)

- Create a new `Dashboard` screen/widget.
- Use `RepoAnalyzer` to fetch stats asynchronously on load.
- Use `HistoryManager` to fetch recent activity.
- Layout:
  - Top: Summary Cards (Total, Size, MV3%).
  - Middle: Risk Distribution (Bar Chart).
  - Bottom: Recent Activity (DataTable).

### 3. Navigation

- Update `FetchextApp` to switch between `Dashboard` and `Browser` modes.
- Add a sidebar or tabs for navigation.

### 4. Testing

- Unit tests for the Dashboard widget (mocking stats).

## Verification

- Run `fext ui` and verify the dashboard loads with correct data.
