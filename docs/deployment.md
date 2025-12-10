# Deployment

`fetchext` is designed to scale from single-user usage to enterprise deployment and repository management.

## Docker

We provide an official Docker image for containerized usage.

```bash
docker run --rm -v $(pwd):/app/downloads ghcr.io/grok/fetchext download chrome <url> -o /app/downloads
```

### Building Locally

You can build the image yourself using the provided `Dockerfile`:

```bash
docker build -t fetchext .
```

## Local Repository Management

### Mirroring

Keep a local folder synchronized with a list of required extensions. This is ideal for maintaining an approved list of extensions for an organization.

```bash
fext mirror extensions_list.txt --output-dir ./repo --prune
```

**List Format:**

```text
chrome <id>
firefox <url>
edge <id>
```

### Update Server

You can host your own Chrome/Edge Update Server or Firefox Update Manifest to serve extensions within a private network.

**1. Generate Manifests:**

```bash
fext update-manifest ./repo --base-url http://internal-extensions.corp.com/
```

This creates `update.xml` (Chrome/Edge) and `updates.json` (Firefox).

**2. Serve the Repository:**
`fetchext` includes a simple HTTP server for testing or light usage:

```bash
fext serve -d ./repo -p 8080
```

**3. Configure Browsers:**
Point your enterprise policies (GPO / MDM) to your internal update URL:

- **Chrome/Edge**: `ExtensionInstallForcelist` pointing to `http://.../update.xml`
- **Firefox**: `ExtensionSettings` pointing to `http://.../updates.json`

## CI/CD Integration

### Pre-commit Hook

Audit extensions committed to your repository for security risks and MV3 compatibility.

Add this to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/grok/fetchext
  rev: v1.6.0
  hooks:
    - id: fext-audit
    - id: fext-scan
```

### GitHub Actions

You can use `fetchext` in GitHub Actions to automatically download and analyze extensions.

```yaml
steps:
  - uses: actions/checkout@v3
  - uses: actions/setup-python@v4
    with:
      python-version: '3.11'
  - run: pip install fetchext
  - run: fext audit my-extension.crx
```
