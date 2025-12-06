# CLI Reference

The `fext` command line interface is the primary way to interact with fetchext.

## Global Options

- `-v`, `--verbose`: Enable debug logging.
- `-q`, `--quiet`: Suppress non-error output.
- `--version`: Show version information.

## Commands

### `download`

Download an extension from a Web Store.

```bash
fext download <browser> <url_or_id> [options]
```

**Arguments:**

- `browser`: `chrome`, `edge`, or `firefox`.
- `url_or_id`: The full URL or the extension ID.

**Options:**

- `-o`, `--output <dir>`: Output directory.
- `-x`, `--extract`: Extract the extension after downloading.
- `-m`, `--save-metadata`: Save metadata to a sidecar JSON file.

### `search`

Search for extensions (currently Firefox only).

```bash
fext search <browser> <query> [--json] [--csv]
```

### `inspect`

Inspect a local extension file.

```bash
fext inspect <file> [--json]
```

### `scan`

Scan an extension for vulnerable libraries.

```bash
fext scan <file> [--json] [--csv]
```

### `report`

Generate a Markdown report for an extension.

```bash
fext report <file> [-o <output>]
```

### `batch`

Download multiple extensions from a list.

```bash
fext batch <file> [-o <dir>] [-w <workers>]
```

### `mirror`

Sync a local directory with a list of extensions.

```bash
fext mirror <list_file> [-o <dir>] [--prune]
```

### `stats`

Show statistics for a repository.

```bash
fext stats <dir>
```

### `convert`

Convert extension formats.

```bash
fext convert <input> --to <format>
```

### `analyze`

Analyze extension code.

```bash
fext analyze <file> [--complexity] [--json]
```

### `locales`

Inspect extension locales.

```bash
fext locales <file> [--json]
```
