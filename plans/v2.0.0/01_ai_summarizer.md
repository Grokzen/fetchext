# Plan: AI Summarizer

## Goal

Implement `fext analyze summary <file>` to generate a natural language summary of an extension's functionality using an LLM.

## Design

### 1. Configuration

Add a new `[ai]` section to `config.toml`:

```toml
[ai]
enabled = false
provider = "openai" # or "ollama", "custom"
api_key = "sk-..."
base_url = "https://api.openai.com/v1"
model = "gpt-3.5-turbo"
```

### 2. Core Logic (`src/fetchext/analysis/ai.py`)

- Implement `summarize_extension(file_path: Path) -> str`.
- Extract `manifest.json` and key files (e.g., `background.js`, `content_scripts`) to build a context prompt.
- Truncate content to fit within reasonable token limits.
- Send request to the configured LLM provider using `requests`.

### 3. CLI Integration (`src/fetchext/commands/audit.py`)

- Add `summary` subcommand to `analyze` parser.
- Check if AI is enabled in config; if not, prompt user or error out.
- Print the summary to the console (Markdown rendered).

### 4. Dependencies

- Use existing `requests` library. No new heavy dependencies.

## Implementation Steps

1. Update `src/fetchext/config.py` schema.
2. Create `src/fetchext/analysis/ai.py`.
3. Update `src/fetchext/commands/audit.py`.
4. Add unit tests (mocking the API call).
