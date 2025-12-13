# Plan: JS Sandbox Command

## Goal
Implement `fext sandbox <file.js>` to execute JavaScript files from extensions in a secure, isolated environment.

## Motivation
Security researchers often need to deobfuscate or analyze the behavior of suspicious JavaScript code found in extensions. Running this code directly on the host machine is dangerous. A sandbox allows safe execution with controlled permissions.

## Architecture

### 1. Runtime Selection
- **Primary**: `deno` (if available).
  - Pros: Built-in security model (permissions system), modern JS/TS support.
  - Mode: Run with `--no-prompt` and default deny-all permissions (no net, no read/write, no env).
- **Fallback**: `node` (if available).
  - Pros: Ubiquitous.
  - Cons: Not a security boundary.
  - Mitigation: Use `vm` module (not secure, but better than eval) or warn user heavily.
  - **Decision**: For this "experimental" feature, we will **require Deno** for the "secure" guarantee. If Deno is not found, the command should fail with a helpful message explaining why Deno is needed and how to install it. We will NOT use Node.js as a fallback for "sandbox" because it gives a false sense of security.

### 2. CLI Command
- `fext sandbox <file>`
- Flags:
  - `--allow-net`: Allow network access (optional, default: False).
  - `--allow-read`: Allow file system read (optional, default: False).
  - `--timeout <seconds>`: Max execution time (default: 5s).
  - `--args <args>`: Arguments to pass to the script.

### 3. Implementation Details
- **Module**: `src/fetchext/commands/sandbox.py`
- **Logic**:
  1. Check for `deno` executable.
  2. Construct `deno run` command with appropriate flags.
  3. Execute using `subprocess.run`.
  4. Capture stdout/stderr.
  5. Handle timeouts.

### 4. Integration
- Register command in `src/fetchext/commands/__init__.py` (or `cli.py` dispatch).

## Steps
1. Create `src/fetchext/commands/sandbox.py`.
2. Implement `DenoSandbox` class to handle execution.
3. Register the command in `src/fetchext/commands/sandbox.py` (register function).
4. Add tests (mocking `subprocess.run`).
5. Update `ROADMAP.md` and `CHANGELOG.md`.

## Risks
- User doesn't have Deno. -> Handle gracefully.
- Malicious code escapes Deno? -> Unlikely, but Deno is robust.
- Infinite loops. -> Use timeout.
