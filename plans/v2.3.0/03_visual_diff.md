# Plan: Visual Diff

## Goal

Add a `--visual` flag to the `diff` command to generate an HTML report showing side-by-side comparisons of modified files, specifically focusing on images.

## Requirements

1. **CLI Flag**: Add `--visual` (and optional `--output <file>`) to `fext diff`.
2. **HTML Generation**: Create a self-contained HTML report.
3. **Image Comparison**: Display modified images side-by-side (Old vs New).
4. **Text Comparison**: Display text diffs (using `difflib.HtmlDiff` or similar).
5. **Assets**: Embed images as Base64 to keep the report portable.

## Implementation Steps

### 1. Update `DiffCommand`

- Modify `src/fetchext/commands/diff.py`.
- Add `--visual` boolean flag.
- Add `--output` string flag (default: `diff_report.html`).
- If `--visual` is set, call the new visual diff generator instead of the console printer.

### 2. Create `VisualDiffGenerator`

- Create `src/fetchext/analysis/visual_diff.py`.
- Class `VisualDiffGenerator`.
- Method `generate(diff_result: DiffResult, output_path: Path)`.
- Logic:
  - Iterate through `diff_result`.
  - For text files: Generate HTML diff fragment.
  - For images: Read both files, convert to Base64, create an `<img>` tag pair.
  - Use a simple HTML template (embedded string or separate file if needed, but string is easier for packaging).
  - Write to `output_path`.

### 3. HTML Template

- Simple CSS for side-by-side layout.
- Sections:
  - Summary (Files added, removed, modified).
  - Modified Files (Loop).

### 4. Testing

- Unit test for `VisualDiffGenerator` (mocking file reads).
- Integration test for `fext diff --visual`.

## Verification

- Run `fext diff --visual old.crx new.crx`.
- Open the generated HTML file and verify layout.
