#!/bin/bash
set -e

# Create a clean test directory
TEST_DIR="smoke_test_output"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

echo "=== 1. Version Check ==="
fext --version

echo "=== 2. Config List ==="
fext config show

echo "=== 3. Download Extension (Chrome) ==="
# Using Postman Interceptor ID: aicmkgpgakddgnaphhhpliifpcfhicfo
# We use --save-metadata to test that too
fext download chrome aicmkgpgakddgnaphhhpliifpcfhicfo -o "$TEST_DIR" --save-metadata

FILE="$TEST_DIR/aicmkgpgakddgnaphhhpliifpcfhicfo.crx"

if [ ! -f "$FILE" ]; then
    echo "Error: Download failed, file not found: $FILE"
    exit 1
fi

echo "=== 4. Inspect Extension ==="
fext inspect "$FILE"

echo "=== 5. Preview Extension ==="
fext preview "$FILE"

echo "=== 6. Extract Extension ==="
fext extract "$FILE" -o "$TEST_DIR/extracted"

echo "=== 7. Report Generation ==="
fext report "$FILE"

echo "=== 8. Analysis: Complexity ==="
# Analyze the extracted directory or the CRX? The command usually takes a file or directory.
# Let's try the extracted directory for complexity as it needs to read JS files.
# Wait, the help says `fext analyze --complexity <file>`. It probably handles CRX by mounting/reading it or expects a JS file?
# Let's check the help or code.
# core.py: analyze_complexity(file_path)
# It seems it can handle the archive.
fext analyze --complexity "$FILE"

echo "=== 9. Analysis: Entropy ==="
fext analyze --entropy "$FILE"

echo "=== 10. Analysis: Domains ==="
fext analyze --domains "$FILE"

echo "=== 11. Dependency Scan ==="
fext scan "$FILE"

echo "=== 12. Verify Hash (Integrity) ==="
# We need the hash first. Let's calculate it.
HASH=$(sha256sum "$FILE" | awk '{print $1}')
echo "Calculated Hash: $HASH"
# Now verify it (re-downloading effectively, or just verifying existing? The command is `download --verify-hash`)
# But we can't verify an existing file with `download` command easily without downloading again.
# Is there a `verify` command?
# Yes, `fext verify <file>` but that's for CRX signature.
# The integrity check is part of download.
# Let's try downloading again with the hash.
fext download chrome aicmkgpgakddgnaphhhpliifpcfhicfo -o "$TEST_DIR" --verify-hash "$HASH"

echo "=== 13. Filename Sanitization Test ==="
# We can't easily force a bad filename from the CLI without a mock server, 
# but we can check if the previous download produced a clean filename.
ls -l "$TEST_DIR"

echo "=== Smoke Test Completed Successfully ==="
