# Plan: Export to STIX

## Goal

Implement STIX 2.1 export capability to generate Threat Intelligence objects for detected indicators (hashes, domains, IPs).

## Objectives

1. Add `stix2` dependency.
2. Create `src/fetchext/analysis/stix.py` to handle STIX object generation.
3. Implement `StixGenerator` class.
4. Integrate with `fext report` or create `fext export` command.
    * The roadmap says `fext export --stix <file>`, but `fext report` might be a better place if it's just another format.
    * However, `fext export` implies converting data to external formats.
    * Let's stick to `fext export` as a new command group if it doesn't exist, or add to `report`.
    * Actually, `fext report` already has `--json` and `--html`. Adding `--stix` makes sense there.
    * But the roadmap explicitly says `fext export --stix`. I'll check if `export` command exists.

## Implementation Details

### 1. Dependencies

Add `stix2` to `pyproject.toml`.

### 2. `StixGenerator` Class

* Input: Analysis results (metadata, domains, hashes).
* Output: STIX 2.1 Bundle JSON.
* Objects to generate:
  * `Indicator`: For malicious domains/hashes (if flagged).
  * `ObservedData`: For all extracted domains/hashes.
  * `Malware`: If YARA matches found.
  * `Report`: Wrapping everything.

### 3. CLI Integration

* Check if `fext export` exists. If not, create it.
* Or add `--stix` to `fext report`.
* Let's follow the roadmap: `fext export --stix <file>`.

## Risks

* STIX complexity: STIX 2.1 is complex. We should keep it simple (Indicators, Observables).

## Verification

* Validate generated JSON against STIX 2.1 schema (using `stix2` library validation).
