# Implementation Loop Prompt

**Objective**: Complete **ALL** remaining items for the current target release version in `ROADMAP.md`.

**CRITICAL INSTRUCTION**:
You are an autonomous agent. You must loop through **ALL** items in the target release. **DO NOT STOP** after completing one or two items. **DO NOT ASK** for user permission to proceed to the next item. Continue the loop until the entire release section is marked as completed (`[x]`).

**Workflow Loop**:
Repeat these steps for every incomplete item:

1. **Identify Task**:
    * Read `ROADMAP.md`.
    * Identify the next unchecked (`[ ]`) item in the current target release version.
    * If no items remain in this version, break the loop and proceed to **Finalization**.

2. **Plan**:
    * Create a detailed plan file in `plans/` (e.g., `plans/v1.2.0_04_config_management.md`).

3. **Implement & Verify**:
    * Write the code.
    * Write unit tests (`pytest`).
    * **Verify**: Run the tests and manually execute the command to ensure it works.
    * Verify the code by running both unit/integration tests via pytest, but you also should test all code via `make ci` command, and you should always test all features the way that a human would do via the terminal and calling the tool

4. **Document**:
    * **Update `README.md`**: Document new commands/flags.
    * **Update `CHANGELOG.md`**: Add entry under current version.
    * **Update `.github/copilot-instructions.md`**: If architecture changed.

5. **Update Roadmap**:
    * Edit `ROADMAP.md`: Change the item from `[ ]` to `[x]`.

6. **Commit**:
    * Run linting (`ruff`, `markdownlint`).
    * Stage **ALL** changes: `git add .` (Ensure `ROADMAP.md` is included).
    * Commit: `git commit -m "feat: <description>"`

7. **Loop**:
    * **IMMEDIATELY** return to Step 1.

**Finalization** (Only when all items are `[x]`):

1. Verify `pyproject.toml` version matches the target release.
2. If not, bump the version and commit: `git commit -m "chore: release vX.Y.Z"`.
3. Report: "Release vX.Y.Z is complete. All items implemented and verified."
