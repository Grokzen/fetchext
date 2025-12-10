# Analysis & Forensics

`fetchext` provides a suite of tools for analyzing browser extensions, ranging from basic metadata inspection to deep forensic analysis of source code and behavior.

## Risk Assessment

### Permission Scoring

The `risk` command calculates a "Privacy Risk Score" based on the permissions requested in the manifest.

```bash
fext risk <file>
```

**Scoring Logic:**

- **Critical (10)**: `<all_urls>`, `debugger`, `webRequestBlocking`, `proxy`.
- **High (7-9)**: `tabs`, `history`, `bookmarks`, `cookies`.
- **Medium (4-6)**: `storage`, `notifications`, `geolocation`.
- **Low (1-3)**: `alarms`, `idle`.

**Toxic Combinations:**
The analyzer also looks for dangerous combinations of permissions that amplify risk, such as:

- `tabs` + `cookies` + `<all_urls>` (Session Hijacking risk)
- `webRequest` + `webRequestBlocking` (Man-in-the-Middle risk)

### Content Security Policy (CSP)

The `audit` command checks the extension's CSP for weak configurations that could allow Cross-Site Scripting (XSS) or code injection.

```bash
fext audit <file>
```

**Checks:**

- Usage of `unsafe-eval` (allows `eval()`).
- Usage of `unsafe-inline` (allows inline scripts).
- Missing `object-src` restrictions.
- overly permissive `connect-src`.

## Code Analysis

### Entropy Analysis

High entropy in files often indicates packed, obfuscated, or encrypted code, which is common in malware trying to hide its payload.

```bash
fext analyze --entropy <file>
```

The tool calculates the Shannon entropy (0-8) for every file in the archive.

- **> 7.5**: Likely compressed or encrypted.
- **> 6.0**: Potential obfuscated code (if it's a JS file).

### Cyclomatic Complexity

To detect obfuscated code that hasn't been packed, `fetchext` measures the cyclomatic complexity of JavaScript functions.

```bash
fext analyze --complexity <file>
```

Obfuscated code often has abnormally high complexity (nested loops, conditionals) or very long single-line functions.

### YARA Scanning

Scan extension files against custom or standard YARA rules to detect known malware signatures.

```bash
fext analyze --yara /path/to/rules/ <file>
```

You can provide a single `.yar` file or a directory containing multiple rule files.

### Secret Scanning

The `scan --secrets` command searches source code for accidentally committed credentials.

```bash
fext analyze --secrets <file>
```

**Detects:**

- AWS Access Keys
- Google API Keys
- Slack Tokens
- Stripe Keys
- Generic high-entropy strings resembling keys.

## Network Forensics

### Domain Extraction

To understand where an extension is sending data, use the domain extractor. It parses JavaScript, HTML, CSS, and JSON files to find all URLs and domains.

```bash
fext analyze --domains <file>
```

This is useful for identifying tracking endpoints, C2 servers, or external dependencies.

## Visualization

### Timeline View

The `timeline` command visualizes the modification dates of files within the archive.

```bash
fext timeline <file>
```

**Forensic Use:**

- Identify files modified *after* the official build time.
- Detect "timestomping" (if dates are impossibly old or future).
- See the development cadence.

### Dependency Graph

Generate a visual graph of internal file dependencies (imports, requires, script tags).

```bash
fext graph <file>
```

This produces a DOT file that can be rendered with Graphviz to visualize the architecture of the extension.

## Localization Analysis

### Locale Inspection

The `locales` command inspects the `_locales` directory to identify supported languages and message counts.

```bash
fext locales <file>
```

**Analysis:**

- Identifies the `default_locale` specified in the manifest.
- Lists all supported locale codes (e.g., `en_US`, `fr`, `es`).
- Counts the number of translation messages for each locale, helping to identify incomplete translations.
