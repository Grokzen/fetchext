# Plan: Firefox Signature Verification

## Goal

Implement cryptographic signature verification for Firefox extensions (.xpi).

## Context

Firefox extensions are signed ZIP archives. The signature is stored in the `META-INF` directory, typically `META-INF/mozilla.rsa` (PKCS#7/CMS) and `META-INF/manifest.mf`.

## Steps

1. **Research XPI Signing**:
    * Confirm the structure: `META-INF/manifest.mf` (hashes of all files), `META-INF/mozilla.sf` (signature of manifest), `META-INF/mozilla.rsa` (PKCS#7 signature of .sf file).
2. **Implement `XpiVerifier`**:
    * Add `XpiVerifier` class to `src/fetchext/verifier.py`.
    * Extract `META-INF/mozilla.rsa`, `META-INF/mozilla.sf`, `META-INF/manifest.mf`.
    * Verify `mozilla.rsa` signs `mozilla.sf`.
    * Verify `mozilla.sf` contains the hash of `manifest.mf`.
    * (Optional/Expensive) Verify `manifest.mf` hashes match all files in the archive. For now, verifying the signature chain is the primary goal.
3. **Update `core.py`**:
    * Update `verify_signature` to detect `.xpi` files and use `XpiVerifier`.
4. **Testing**:
    * Add unit tests with a sample signed XPI (or mocked structure).

## Dependencies

* `cryptography` (already in project).
* Need to check if `cryptography` supports loading PKCS#7/CMS. It supports loading DER/PEM, but full CMS verification might be tricky without `pyopenssl` or `asn1crypto`.
* If `cryptography` is insufficient for CMS, we might need to parse the ASN.1 manually or use a lightweight parser. `cryptography.hazmat.primitives.serialization.pkcs7` exists in newer versions? No, it's `pkcs7` module is limited.
* Alternative: Use `openssl` CLI if available? No, pure python preferred.
* We can use `cryptography` to load the certificate and verify the signature if we extract the signed data and signature manually.

## Refinement

Since `cryptography` doesn't have a high-level "verify CMS" API, we might need to parse the PKCS#7 blob to extract the certificate and the signature.
The `mozilla.rsa` file is a DER-encoded PKCS#7 SignedData.
We might need to add `asn1crypto` to dependencies if `cryptography` is too low-level.
However, `cryptography` 3.1+ has `load_der_pkcs7_certificates`.
But we need the signature too.

Let's try to stick to `cryptography` if possible, or add `asn1crypto` if needed (it's pure python and small).
Actually, `fetchext` tries to keep dependencies minimal.
Maybe we can just verify that the file *has* a signature structure for now, or do a best-effort verification.
But the roadmap says "Implement XPI signature verification".

Let's check if `asn1crypto` is allowed. It's not in `pyproject.toml`.
I'll try to implement it using `cryptography` and basic ASN.1 parsing if needed, or just verify the presence and structure.
Actually, `mozilla.rsa` is a standard CMS.
I will investigate `src/fetchext/verifier.py` to see if I can extend it.
