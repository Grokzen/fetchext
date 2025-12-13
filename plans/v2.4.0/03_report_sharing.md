# Plan: Report Sharing

## Goal

Add `fext share <report.html>` to automatically upload reports to a configured destination (e.g., GitHub Gist, S3, or a pastebin) and generate a shareable link for team collaboration.

## Motivation

Currently, reports are generated locally. Sharing them with teammates requires manual file transfer. This feature streamlines collaboration by providing a one-step upload and share mechanism.

## Implementation Steps

### 1. Create `src/fetchext/commands/share.py`

- Implement the `share` command.
- Support multiple providers (initially GitHub Gist, maybe Pastebin).
- Use `config.toml` for authentication tokens.

### 2. Create `src/fetchext/sharing/`

- Create a `BaseUploader` abstract class.
- Implement `GistUploader`.
- Implement `PastebinUploader` (optional for now).

### 3. Update `config.toml` Schema

- Add `[sharing]` section.
- `provider = "gist"`
- `github_token = "..."`

### 4. Register Command

- Update `src/fetchext/cli.py` (or wherever commands are registered) to include `share`.

## Testing Strategy

- **Unit Test**: Mock the network requests to GitHub API.
- **Integration Test**: Verify the flow from command to uploader.

## Documentation

- Update `docs/cli.md` with `fext share` usage.
- Update `docs/configuration.md` with `[sharing]` section details.
