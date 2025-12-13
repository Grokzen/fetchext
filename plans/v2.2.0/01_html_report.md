# Plan: HTML Report

## Goal

Implement `fext report --html <file>` to generate a standalone, interactive HTML report with charts and graphs.

## Details

- The report should aggregate data from:
  - Metadata (manifest)
  - Risk Analysis
  - MV3 Audit
  - Complexity
  - Entropy
  - Domains
  - Secrets
  - Licenses
- It should be a single HTML file.
- Use embedded CSS/JS for styling and interactivity.
- Use Chart.js (via CDN or embedded) for visualizations (Risk distribution, File types).

## Implementation Steps

1. Modify `src/fetchext/commands/report.py` (or create it if it doesn't exist, currently `report` is likely in `audit.py` or its own file).
    - Check `src/fetchext/commands/` to see where `report` is.
2. Create `src/fetchext/reporting/html_generator.py`.
    - Class `HtmlReportGenerator`.
    - Methods to generate sections (Header, Summary, Risk, File Analysis).
    - Method `generate(data) -> str`.
3. Update `fext report` command to accept `--html` flag.
4. Add tests.

## Dependencies

- None (use standard library string formatting).
- External: Chart.js (CDN link).
