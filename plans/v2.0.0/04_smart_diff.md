# Smart Diff Implementation Plan

## Goal

Enhance the `fext diff` command to provide smarter comparisons, specifically for images and code whitespace.

## Problem

Currently, `fext diff` likely does a simple file presence/hash check.

- It doesn't show *what* changed in text files (just that they changed).
- It doesn't handle image changes visually or intelligently.
- It flags whitespace-only changes as modifications, which can be noisy.

## Solution

1. **Whitespace Ignoring**: Add an option to ignore whitespace changes when comparing text files (JS, CSS, HTML, JSON).
2. **Image Comparison**: Detect if an image has changed visually or just metadata. (Maybe too complex for CLI, but we can at least report dimensions/size changes).
3. **Detailed Text Diff**: For text files, show a unified diff snippet if requested.

## Implementation Details

### 1. Dependencies

- No new heavy dependencies.
- `difflib` (standard library) for text diffs.
- `Pillow` (already a dependency) for image analysis.

### 2. Core Logic (`src/fetchext/diff.py`)

- Update `DiffEngine` (or equivalent class/function).
- Add `ignore_whitespace` parameter.
- Add `compare_images` logic.
- Implement `generate_text_diff` to return unified diffs.

### 3. CLI (`src/fetchext/commands/inspect.py`)

- Update `diff_parser` arguments:
  - `--ignore-whitespace` / `-w`: Ignore whitespace in text comparisons.
  - `--unified` / `-u`: Show unified diff for text files (limit lines).
  - `--images`: Enable detailed image comparison.

### 4. Testing

- Unit tests for `diff_extensions` with whitespace variations.
- Unit tests for image comparison.

## Verification

- Create two dummy extensions with:
  - `script.js` (original) vs `script.js` (whitespace changed).
  - `image.png` (original) vs `image.png` (resized).
- Run `fext diff old.zip new.zip -w` and verify `script.js` is not flagged (or flagged as whitespace-only).
