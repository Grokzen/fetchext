# Implementation Loop Prompt

**Objective**: Complete **ALL** remaining items for the current target release version in `ROADMAP.md`.

**Loop Instructions**:
Repeat the following steps for *every single incomplete item* in the target release version. Do not stop after a fixed number of items; continue until the entire release section is marked as completed (`[x]`).

1. **Identify Task**:
    * Read `ROADMAP.md`.
    * Identify the next unchecked (`[ ]`) item in the current target release version.
    * If no items remain in this version, **STOP** and report completion.

2. **Plan**:
    * Analyze the repository state.
    * Create a detailed plan file in `plans/` (e.g., `plans/v1.2.0_04_config_management.md`).
    * Ensure the plan covers implementation, testing, and documentation.

3. **Implement & Verify**:
    * Write the code.
    * Write unit tests (`pytest`).
    * **Crucial**: Verify functionality manually in the terminal (run the command, check output).
    * Fix any issues found during verification.

4. **Documentation & Cleanup**:
    * **Update `README.md`**: Ensure new commands/flags are documented with examples.
    * **Update `CHANGELOG.md`**: Add an entry under the current version.
    * **Update `docs/`**: If a docs folder exists, update relevant pages.
    * **Update `.github/copilot-instructions.md`**: If architectural decisions changed.

5. **Mark Complete**:
    * **Update `ROADMAP.md`**: Change the item from `[ ]` to `[x]`.

6. **Commit**:
    * Run linting (`ruff`, `markdownlint`).
    * Git commit with a descriptive message (e.g., `feat: implement config management`).

7. **Loop**:
    * Return to Step 1 immediately. Do not ask for user input between tasks unless blocked.

**Final Output**:
Once all items in the release are checked off, report back that the release is ready.
