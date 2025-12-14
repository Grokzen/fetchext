# Plan: Dynamic Analysis Sandbox

## Goal

Implement dynamic analysis capabilities using `playwright` to launch extensions in a headless browser and capture runtime behavior.

## Objectives

1. Install `playwright` dependency.
2. Create `src/fetchext/analysis/dynamic.py` to handle the browser automation.
3. Launch a headless Chromium instance with the extension loaded.
4. Capture:
    * Screenshots of the extension popup/options page.
    * Console logs (errors, warnings).
    * Network requests (domains contacted).
5. Integrate with `fext analyze` command.
6. Update reports to include dynamic analysis data.

## Implementation Details

### 1. Dependencies

Add `playwright` to `pyproject.toml` (optional dependency? or dev?).
Since it requires browser binaries, maybe keep it as an optional extra `fetchext[dynamic]`.

### 2. `DynamicAnalyzer` Class

* `__init__(self, extension_path)`
* `async run(self)`: Main entry point.
* `async _capture_screenshots(self, page)`
* `async _monitor_network(self, page)`
* `async _monitor_console(self, page)`

### 3. CLI Integration

* Add `dynamic` subcommand to `fext analyze`.
* `fext analyze dynamic <file> [--headless/--headed]`

### 4. Reporting

* Save screenshots to `analysis/screenshots/`.
* Save logs to `analysis/logs.json`.
* Save network activity to `analysis/network.json`.

## Risks

* Playwright browser installation might be heavy.
* Extensions might require user interaction to trigger malicious behavior.
* Sandboxing: Running unknown extensions is risky. We should warn the user or recommend running in a VM/Container.

## Verification

* Test with a benign extension (e.g., uBlock Origin).
* Verify screenshots are captured.
* Verify network requests are logged.
