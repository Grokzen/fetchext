# Plan: TUI E2E Testing

## Goal

Implement automated end-to-end tests for the TUI using `textual`'s `Pilot` testing harness to verify user interactions and prevent UI regressions.

## Motivation

The TUI is a complex interactive component. Manual testing is slow and error-prone. Automated E2E tests ensure that key flows (search, download, navigation) work as expected.

## Implementation Steps

### 1. Create `tests/tui/`

- [x] Create a dedicated directory for TUI tests.

### 2. Create `tests/tui/test_app.py`

- [x] Use `textual.pilot.Pilot` to drive the application.
- [x] Test scenarios:
  - App startup.
  - Tab switching (Home -> Search -> Download).
  - Search input and submission.
  - Browser selection.
  - Quit application.

### 3. Update `Makefile`

- [x] Add a target for running TUI tests specifically (if needed). (Not strictly needed as `make test` runs all tests)

## Testing Strategy

- **E2E Test**: Simulate key presses and verify screen content.
- **Mocking**: Mock network calls to avoid hitting real Web Stores during UI tests.

## Documentation

- Update `CONTRIBUTING.md` (if it exists) or `README.md` with instructions on running UI tests.
