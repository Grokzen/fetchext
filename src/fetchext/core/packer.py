import struct
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from fetchext.core.protobuf  import SimpleProtobuf
from fetchext.core.exceptions  import ExtensionError
from fetchext.plugins.hooks  import HookManager, HookContext
from fetchext.data.config  import get_config_path, load_config

logger = logging.getLogger(__name__)


class ExtensionPacker:
    """
    Packs a directory into a signed CRX3 file.
    """

    CRX_MAGIC = b"Cr24"
    CRX_VERSION = 3

    def __init__(self):
        pass

    def generate_key(self, output_path: Path) -> rsa.RSAPrivateKey:
        """
        Generates a new RSA private key and saves it to output_path.
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        with open(output_path, "wb") as f:
            f.write(pem)

        logger.info(f"Generated new private key: {output_path}")
        return private_key

    def load_key(self, key_path: Path) -> rsa.RSAPrivateKey:
        """
        Loads an RSA private key from a PEM file.
        """
        with open(key_path, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

    def pack(
        self, source_dir: Path, output_path: Path, key_path: Optional[Path] = None
    ) -> Path:
        """
        Packs the source directory into a CRX3 file.
        If key_path is not provided, generates a new key in the output directory.
        """
        source_dir = Path(source_dir)
        output_path = Path(output_path)

        if not source_dir.exists() or not source_dir.is_dir():
            raise ExtensionError(f"Source directory not found: {source_dir}")

        # Initialize hooks
        config_dir = get_config_path().parent
        hooks_dir = config_dir / "hooks"
        hook_manager = HookManager(hooks_dir)
        try:
            config = load_config()
        except Exception:
            config = {}

        # Run pre-pack hook
        ctx = HookContext(
            extension_id="unknown",
            browser="unknown",
            file_path=source_dir,
            config=config,
        )
        hook_manager.run_hook("pre_pack", ctx)

        if ctx.cancel:
            logger.info("Packing cancelled by pre_pack hook.")
            return None

        # Handle Key
        if key_path:
            key_path = Path(key_path)
            if not key_path.exists():
                raise ExtensionError(f"Key file not found: {key_path}")
            private_key = self.load_key(key_path)
        else:
            # Generate key next to output file if not exists, or use existing if name matches?
            # Default: <output_name>.pem
            key_path = output_path.with_suffix(".pem")
            if key_path.exists():
                logger.info(f"Using existing key found at {key_path}")
                private_key = self.load_key(key_path)
            else:
                private_key = self.generate_key(key_path)

        # 1. Create ZIP
        zip_path = output_path.with_suffix(".zip.tmp")
        try:
            shutil.make_archive(str(zip_path.with_suffix("")), "zip", source_dir)
            # make_archive adds .zip extension
            real_zip_path = zip_path.with_suffix(".zip")
            if real_zip_path.exists():
                real_zip_path.rename(zip_path)

            with open(zip_path, "rb") as f:
                zip_data = f.read()
        finally:
            if zip_path.exists():
                zip_path.unlink()

        # 2. Prepare Public Key
        public_key = private_key.public_key()
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Calculate CRX ID
        sha = hashlib.sha256(pub_bytes).digest()
        crx_id = sha[:16]  # Raw bytes for SignedData

        # Update context with ID
        hex_str = crx_id.hex()
        trans_map = str.maketrans("0123456789abcdef", "abcdefghijklmnop")
        ctx.extension_id = hex_str.translate(trans_map)

        # 3. Create SignedData
        # Field 1: crx_id (16 bytes)
        signed_data = SimpleProtobuf.encode({1: [crx_id]})

        # 4. Sign
        # Signature = Sign( "CRX3 SignedData\x00" + len(signed_data) + signed_data + zip_data )
        prefix = b"CRX3 SignedData\x00"
        len_bytes = struct.pack("<I", len(signed_data))

        data_to_sign = prefix + len_bytes + signed_data + zip_data

        signature = private_key.sign(data_to_sign, padding.PKCS1v15(), hashes.SHA256())

        # 5. Create AsymmetricKeyProof
        # Field 1: public_key
        # Field 2: signature
        proof = SimpleProtobuf.encode({1: [pub_bytes], 2: [signature]})

        # 6. Create CrxFileHeader
        # Field 10000: sha256_with_rsa (repeated) -> [proof]
        # Field 10001: signed_header_data -> signed_data
        header = SimpleProtobuf.encode({10000: [proof], 10001: [signed_data]})

        # 7. Write CRX
        with open(output_path, "wb") as f:
            f.write(self.CRX_MAGIC)
            f.write(struct.pack("<I", self.CRX_VERSION))
            f.write(struct.pack("<I", len(header)))
            f.write(header)
            f.write(zip_data)

        logger.info(f"Packed extension to {output_path}")

        # Run post-pack hook
        ctx.file_path = output_path
        hook_manager.run_hook("post_pack", ctx)

        return output_path


def pack_extension(source_dir, output_path=None, key_path=None):
    """
    Helper function to pack an extension.
    """
    packer = ExtensionPacker()
    if not output_path:
        source_dir = Path(source_dir)
        output_path = source_dir.with_suffix(".crx")

    return packer.pack(source_dir, output_path, key_path)
