# Plan: Property-Based Testing for CrxDecoder

## Goal
Enhance the robustness of `CrxDecoder` by implementing advanced property-based tests using `hypothesis`. The goal is to verify that the parser correctly handles a wide range of valid and invalid CRX3 header structures, ensuring it doesn't crash or behave unexpectedly.

## Objectives
1.  Create a `hypothesis` strategy to generate structured CRX3 headers.
    *   Valid Magic (`Cr24`) vs Invalid Magic.
    *   Valid Version (`3`) vs Invalid Versions.
    *   Valid Header Lengths vs Invalid/Overflow Lengths.
    *   Valid/Invalid Protobuf data (mocked).
2.  Implement tests that verify:
    *   **Round-trip properties**: If we construct a valid CRX, can we parse it back?
    *   **Error handling**: Does it raise the correct exceptions (`ValueError`, `struct.error`) for invalid inputs?
    *   **Invariants**: `zip_offset` should always be calculated correctly based on header length.
3.  Increase `max_examples` for deeper coverage (configurable via CI/CD env vars).

## Implementation Details

### 1. Define Strategies
We need a custom strategy `crx_strategy()` that produces:
- `magic`: 4 bytes (usually `Cr24`)
- `version`: 4 bytes (integer)
- `header_length`: 4 bytes (integer)
- `header_data`: binary data of length `header_length`

### 2. Test Cases
- `test_crx_valid_structure`: Generate valid CRX structures and ensure `get_zip_offset` returns the expected value (`magic + version + length_field + header_data`).
- `test_crx_invalid_magic`: Generate CRX with invalid magic and ensure `ValueError` is raised.
- `test_crx_invalid_version`: Generate CRX with version != 3 and ensure `ValueError` is raised.
- `test_crx_header_length_mismatch`: Generate CRX where file size < header length.

### 3. Location
- Update `tests/fuzz/test_crx_fuzz.py`.

## Verification
- Run `pytest tests/fuzz/test_crx_fuzz.py` and ensure it passes.
- Check coverage.
