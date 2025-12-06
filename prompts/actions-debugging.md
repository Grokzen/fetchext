# GitHub Actions Debugging Workflow

This guide describes the standard operating procedure for debugging and fixing GitHub Actions CI failures using the `gh` CLI.

## 1. Fetch & Analyze Logs

Instead of guessing, always fetch the actual failure logs from GitHub.

1. **Find the latest failed run:**

   ```bash
   gh run list --limit 1
   ```

   *Note the `RUN_ID` of the failed workflow.*

2. **Download the logs:**

   ```bash
   gh run view <RUN_ID> --log-failed > failure_log.txt
   ```

   *Alternatively, use `--log` for the full log if context is missing.*

3. **Analyze the log:**
   Read `failure_log.txt` to pinpoint the exact error (e.g., a specific test failure, linting error, or build issue).

## 2. The Debug Loop

Once the error is identified, follow this loop:

1. **Reproduce Locally**:
   Attempt to reproduce the error using local tools (`make test`, `make lint`, etc.).
   *If it passes locally but fails remotely, check for environment differences (Python version, dependencies).*

2. **Implement Fix**:
   Modify the code to resolve the issue.

3. **Verify Fix**:
   Run the relevant local tests again to ensure the fix works and doesn't break anything else.

4. **Commit Changes**:
   Stage and commit the fix. **DO NOT PUSH**.

   ```bash
   git add .
   git commit -m "fix: <description of fix>"
   ```

5. **Repeat**:
   If there were multiple errors in the log, repeat the process until all are addressed.

## 3. Final Handoff

Once the fix is verified and committed:

1. Delete any temporary log files (`rm failure_log.txt`).
2. Inform the user that the fix is committed and ready for them to push.
