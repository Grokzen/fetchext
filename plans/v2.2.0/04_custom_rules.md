# Plan: Custom Rules

## Goal

Support a YAML-based rules engine for defining custom scan patterns without writing full Python plugins.

## Details

- Rules defined in YAML.
- Support regex patterns.
- Integration with `fext scan`.

## Implementation Steps

1. Create `src/fetchext/analysis/rules.py`.
    - Class `RuleEngine`.
    - Method `load_rules(path)`.
    - Method `scan(file_path)`.
2. Update `src/fetchext/commands/audit.py` (where `scan` is).
    - Add `--custom <rules.yaml>` argument.
    - Call `RuleEngine`.

## Rule Format

```yaml
rules:
  - id: my-rule
    description: Detects something
    severity: high
    pattern: "regex_here"
```
