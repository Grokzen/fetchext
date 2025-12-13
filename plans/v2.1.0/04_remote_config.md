# Plan: Remote Config

## Goal

Implement `fext config --remote <url>` to load configuration from a remote URL.

## Problem

Teams want to share standard configurations (e.g., proxy settings, blocked permissions).

## Solution

Fetch a TOML file from a URL and merge it with the local config.

## Implementation Details

### 1. CLI Command (`src/fetchext/commands/config.py`)

- Add `--remote <url>` argument.

### 2. Core Logic

- Use `requests` to fetch the URL.
- Validate TOML structure.
- Save to `~/.config/fext/config.toml` (or a separate `remote.toml` that overrides).
- For now, just overwrite/merge into main config.

## Verification

- Mock HTTP server serving a config file.
- Run `fext config --remote http://localhost/config.toml`.
- Verify local config is updated.
