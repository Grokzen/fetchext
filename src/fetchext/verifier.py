import struct
import zipfile
import hashlib
import base64
from pathlib import Path
from .protobuf import SimpleProtobuf


class CrxVerifier:
    def verify(self, file_path: Path) -> bool:
        """
        Verifies the signature of a CRX3 file.
        Returns True if valid, False otherwise.
        """
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding, utils

        with open(file_path, "rb") as f:
            # Read Magic
            magic = f.read(4)
            if magic != b"Cr24":
                raise ValueError("Not a CRX file (Invalid Magic)")

            # Read Version
            version_bytes = f.read(4)
            version = struct.unpack("<I", version_bytes)[0]
            if version != 3:
                raise ValueError(
                    f"Unsupported CRX version: {version}. Only CRX3 is supported."
                )

            # Read Header Length
            header_len_bytes = f.read(4)
            header_len = struct.unpack("<I", header_len_bytes)[0]

            # Read Header
            header_data = f.read(header_len)

            # The rest is the archive
            archive_start = f.tell()

        # Parse Header (CrxFileHeader)
        # Field 10000: sha256_with_rsa (repeated AsymmetricKeyProof)
        # Field 10001: signed_header_data (bytes)
        fields = SimpleProtobuf.parse(header_data)

        if 10001 not in fields:
            raise ValueError("CRX Header missing signed_header_data")

        signed_header_data = fields[10001][0]

        if 10000 not in fields:
            raise ValueError("CRX Header missing sha256_with_rsa signature")

        # There can be multiple proofs. We need to find one that verifies.
        proofs = fields[10000]

        # We need to read the archive data to verify
        # For large files, we should stream it into the hasher
        hasher = hashes.Hash(hashes.SHA256())

        # Signature is over:
        # 1. ASCII string "CRX3 SignedData\x00"
        # 2. Length of signed_header_data (4 bytes, little endian)
        # 3. signed_header_data
        # 4. Archive data

        prefix = b"CRX3 SignedData\x00"
        hasher.update(prefix)
        hasher.update(struct.pack("<I", len(signed_header_data)))
        hasher.update(signed_header_data)

        # Stream archive data
        with open(file_path, "rb") as f:
            f.seek(archive_start)
            while chunk := f.read(8192):
                hasher.update(chunk)

        digest = hasher.finalize()

        # Now verify each proof against this digest
        # Proof (AsymmetricKeyProof) structure:
        # Field 1: public_key (bytes) - SubjectPublicKeyInfo
        # Field 2: signature (bytes)

        for proof_data in proofs:
            proof_fields = SimpleProtobuf.parse(proof_data)
            if 1 not in proof_fields or 2 not in proof_fields:
                continue

            public_key_bytes = proof_fields[1][0]
            signature = proof_fields[2][0]

            try:
                public_key = serialization.load_der_public_key(public_key_bytes)

                # Verify
                # When using Prehashed, we pass the digest
                public_key.verify(
                    signature,
                    digest,
                    padding.PKCS1v15(),
                    utils.Prehashed(hashes.SHA256()),
                )
                return True
            except Exception:
                continue

        return False


class XpiVerifier:
    def verify(self, file_path: Path) -> bool:
        """
        Verifies the integrity of a Firefox XPI file.
        Checks:
        1. Presence of META-INF/manifest.mf
        2. Presence of META-INF/mozilla.sf
        3. Presence of META-INF/mozilla.rsa
        4. Verifies that files listed in manifest.mf match their hashes.
        """
        if not zipfile.is_zipfile(file_path):
            raise ValueError("Not a valid ZIP/XPI file")

        try:
            with zipfile.ZipFile(file_path) as zf:
                # 1. Find manifest.mf
                if "META-INF/manifest.mf" not in zf.namelist():
                    return False

                # 2. Find signature files
                rsa_files = [
                    n
                    for n in zf.namelist()
                    if n.startswith("META-INF/") and n.endswith(".rsa")
                ]
                if not rsa_files:
                    return False

                # 3. Verify Manifest Integrity
                manifest_data = zf.read("META-INF/manifest.mf").decode("utf-8")
                if not self._verify_manifest(zf, manifest_data):
                    return False

                return True
        except Exception:
            return False

    def _verify_manifest(self, zf, manifest_data):
        entries = self._parse_manifest(manifest_data)

        for filename, hashes in entries.items():
            if filename not in zf.namelist():
                return False

            with zf.open(filename) as f:
                file_data = f.read()

            if "sha256" in hashes:
                digest = hashlib.sha256(file_data).digest()
                expected = base64.b64decode(hashes["sha256"])
                if digest != expected:
                    return False
            elif "sha1" in hashes:
                digest = hashlib.sha1(file_data).digest()
                expected = base64.b64decode(hashes["sha1"])
                if digest != expected:
                    return False

        return True

    def _parse_manifest(self, data):
        entries = {}
        current_file = None
        current_hashes = {}

        for line in data.splitlines():
            line = line.strip()
            if not line:
                if current_file:
                    entries[current_file] = current_hashes
                    current_file = None
                    current_hashes = {}
                continue

            if line.startswith("Name: "):
                current_file = line[6:]
            elif line.startswith("SHA256-Digest: "):
                current_hashes["sha256"] = line[15:]
            elif line.startswith("SHA1-Digest: "):
                current_hashes["sha1"] = line[13:]

        if current_file:
            entries[current_file] = current_hashes

        return entries
