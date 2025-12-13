# Plan: Extension Packer

## Goal

Add a `pack` command to create signed CRX3 files from a source directory.

## Problem

Developers and researchers often need to repack extensions after modification. Currently, `fetchext` can only download and extract, not repack.

## Solution

Implement a `pack` command that:

1. Zips the directory.
2. Generates or uses an existing private key (RSA).
3. Signs the ZIP.
4. Wraps it in a CRX3 header.

## Implementation Details

### 1. Core Logic (`src/fetchext/packer.py`)

- `ExtensionPacker` class.
- `generate_key()`: Create a new RSA key if none provided.
- `pack(source_dir, key_path, output_path)`:
  - Create ZIP from `source_dir`.
  - Sign ZIP with key.
  - Construct CRX3 header (Magic, Version, Header Size, Signed Header Data).
  - Write CRX file.

### 2. CLI Command (`src/fetchext/commands/pack.py`)

- `fext pack <directory> [-k <key.pem>] [-o <output.crx>]`
- If `-k` is not provided, generate `key.pem` in the output directory.

### 3. Dependencies

- `cryptography` (already included).
- `protobuf` (for CRX3 header format).

## Verification

- Pack a directory.
- Verify the output CRX using `fext verify`.
- Try to install in Chrome (Developer Mode).
