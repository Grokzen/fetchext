# Plan: Git Integration

## Goal

Implement `fext git init <directory>` to automatically set up a git repository for a downloaded extension.

## Problem

Developers often download extensions to study them. Setting up git manually with the right `.gitignore` is repetitive.

## Solution

Automate `git init`, `.gitignore` creation, and initial commit.

## Implementation Details

### 1. CLI Command (`src/fetchext/commands/git.py`)

- `fext git init <directory>`
- Optional `--commit` flag (default: true) to make the first commit.

### 2. Core Logic (`src/fetchext/git_utils.py`)

- Check if `git` is installed.
- Run `git init`.
- Write `.gitignore` with common extension patterns:
  - `*.crx`
  - `*.pem`
  - `node_modules/`
  - `.DS_Store`
  - `__pycache__/`
- Run `git add .`
- Run `git commit -m "Initial commit (fext)"`

### 3. Dependencies

- `subprocess` (standard lib).

## Verification

- Run `fext git init ./my-extension`.
- Check `.git` exists.
- Check `.gitignore` content.
- Check `git log` has one commit.
