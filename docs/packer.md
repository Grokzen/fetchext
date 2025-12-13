# Extension Packer

Fetchext includes a built-in tool to pack source directories into `.crx` (Chrome Extension) files. This is useful for developers who want to distribute their extensions or for repackaging modified extensions.

## Usage

To pack an extension directory:

```bash
fext pack <source_directory> [options]
```

### Arguments

- `source_directory`: The path to the directory containing the extension source code (must contain a `manifest.json`).

### Options

- `--pem <path>`: Path to an existing private key (`.pem`) file. If not provided, a new key will be generated.
- `--out <path>`: Output filename for the `.crx` file. Defaults to `<directory_name>.crx`.

## Examples

### Basic Packing (Auto-generate Key)

```bash
fext pack ./my-extension
```

This will create:

- `my-extension.crx`: The packed extension.
- `my-extension.pem`: The generated private key (keep this safe!).

### Packing with an Existing Key

If you have already generated a key (e.g., from a previous pack), use it to maintain the same Extension ID:

```bash
fext pack ./my-extension --pem my-extension.pem
```

### Custom Output Name

```bash
fext pack ./my-extension --out release-v1.0.crx
```

## Technical Details

The packer creates **CRX3** format files, which are required by modern browsers.

- **Signing**: Uses RSA-2048 keys.
- **Hashing**: Uses SHA-256.
- **Header**: Includes the standard CRX3 header with public key and signature proofs.

## Hooks

The packing process supports plugins via the `pre_pack` and `post_pack` hooks. See [Plugins](plugins.md) for more details.
