# Plan: Badge Generator

## Goal

Implement `fext badge <file>` to generate SVG badges for risk scores, version, and license.

## Details

- Badges should look like Shields.io badges.
- Output SVG files.
- Types of badges:
  - `risk`: Color-coded by risk level (Safe=Green, Critical=Red).
  - `version`: Blue badge with version number.
  - `license`: License name (if detected).

## Implementation Steps

1. Create `src/fetchext/commands/badge.py`.
2. Register command in `cli.py`.
3. Implement `BadgeGenerator` class in `src/fetchext/reporting/badges.py` (or `reporter.py`).
    - Method `generate_svg(label, message, color) -> str`.
4. Implement `handle_badge` in `badge.py`.
    - Analyze extension to get data.
    - Generate SVGs.
    - Save to `<filename>_<type>.svg`.

## Dependencies

- None (generate SVG string manually).
