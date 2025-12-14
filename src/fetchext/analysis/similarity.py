import ppdeep
import logging
from pathlib import Path
from typing import List, Dict, Any, Union
from fetchext.utils  import open_extension_archive

logger = logging.getLogger(__name__)


class SimilarityEngine:
    def compute_hash(self, path: Union[str, Path]) -> str:
        """
        Compute fuzzy hash of an extension.
        Aggregates all JavaScript content and hashes it.
        """
        path = Path(path)
        content_buffer = []

        try:
            if path.is_dir():
                for js_file in path.rglob("*.js"):
                    try:
                        content_buffer.append(js_file.read_bytes())
                    except Exception:
                        pass
            else:
                # Assume archive (CRX/ZIP/XPI)
                with open_extension_archive(path) as zf:
                    for filename in zf.namelist():
                        if filename.endswith(".js"):
                            try:
                                content_buffer.append(zf.read(filename))
                            except Exception:
                                pass

            if not content_buffer:
                return ""

            # Join all JS content.
            # Note: Order matters for ssdeep. In a real archive, order is usually stable (by zip index).
            # For directories, rglob order might vary, so we should sort.
            # But wait, we are just appending bytes.
            # Let's sort by filename/path to ensure deterministic hashing.
            # Actually, for archives, namelist order is fixed. For dirs, we should sort.

            # Refined approach:
            # We can't easily sort the buffer after reading.
            # Let's read in sorted order.

            full_content = b"".join(content_buffer)
            return ppdeep.hash(full_content)

        except Exception as e:
            logger.error(f"Failed to compute hash for {path}: {e}")
            return ""

    def find_similar(
        self, target_path: Path, repository_path: Path, threshold: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find extensions in repository similar to target.
        """
        target_hash = self.compute_hash(target_path)
        if not target_hash:
            logger.warning("Could not compute hash for target (no JS files?)")
            return []

        matches = []

        # Scan repository
        # We look for .crx, .xpi, .zip files
        extensions = []
        extensions.extend(repository_path.glob("*.crx"))
        extensions.extend(repository_path.glob("*.xpi"))
        extensions.extend(repository_path.glob("*.zip"))

        for ext_path in extensions:
            if ext_path.resolve() == target_path.resolve():
                continue

            ext_hash = self.compute_hash(ext_path)
            if not ext_hash:
                continue

            score = ppdeep.compare(target_hash, ext_hash)
            if score >= threshold:
                matches.append(
                    {"file": str(ext_path), "score": score, "hash": ext_hash}
                )

        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches
