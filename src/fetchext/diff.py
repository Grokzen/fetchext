import json
import io
import re
import jsbeautifier
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from PIL import Image
from .utils import open_extension_archive


@dataclass
class DiffReport:
    old_version: str
    new_version: str
    manifest_changes: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)
    added_files: List[str] = field(default_factory=list)
    removed_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    image_changes: List[Dict[str, Any]] = field(default_factory=list)


class ExtensionDiffer:
    def diff(
        self,
        old_path: Path,
        new_path: Path,
        ignore_whitespace: bool = False,
        ast_diff: bool = False,
    ) -> DiffReport:
        with (
            open_extension_archive(old_path) as old_zf,
            open_extension_archive(new_path) as new_zf,
        ):
            # Manifest Diff
            old_manifest = self._read_manifest(old_zf)
            new_manifest = self._read_manifest(new_zf)

            manifest_changes = self._diff_manifests(old_manifest, new_manifest)

            # File Diff
            old_files = {info.filename: info for info in old_zf.infolist()}
            new_files = {info.filename: info for info in new_zf.infolist()}

            added = []
            removed = []
            modified = []
            image_changes = []

            all_files = set(old_files.keys()) | set(new_files.keys())

            for filename in sorted(all_files):
                if filename not in old_files:
                    added.append(filename)
                elif filename not in new_files:
                    removed.append(filename)
                else:
                    # Check modification
                    old_info = old_files[filename]
                    new_info = new_files[filename]

                    # Compare CRC32
                    if (
                        old_info.CRC != new_info.CRC
                        or old_info.file_size != new_info.file_size
                    ):
                        # Content changed
                        is_modified = True

                        # Check whitespace if requested
                        if ignore_whitespace and self._is_text_file(filename):
                            try:
                                old_content = old_zf.read(filename).decode(
                                    "utf-8", errors="ignore"
                                )
                                new_content = new_zf.read(filename).decode(
                                    "utf-8", errors="ignore"
                                )
                                if self._compare_text_ignore_whitespace(
                                    old_content, new_content
                                ):
                                    is_modified = False
                            except Exception:
                                pass  # Fallback to binary diff

                        # Check AST diff if requested
                        if (
                            ast_diff
                            and is_modified
                            and filename.lower().endswith(".js")
                        ):
                            try:
                                old_content = old_zf.read(filename).decode(
                                    "utf-8", errors="ignore"
                                )
                                new_content = new_zf.read(filename).decode(
                                    "utf-8", errors="ignore"
                                )
                                if self._compare_js_ast(old_content, new_content):
                                    is_modified = False
                            except Exception:
                                pass

                        # Check image changes
                        if is_modified and self._is_image_file(filename):
                            try:
                                img_diff = self._compare_images(
                                    old_zf.read(filename), new_zf.read(filename)
                                )
                                if img_diff:
                                    image_changes.append(
                                        {"file": filename, "diff": img_diff}
                                    )
                            except Exception:
                                pass

                        if is_modified:
                            modified.append(filename)

            return DiffReport(
                old_version=old_manifest.get("version", "unknown"),
                new_version=new_manifest.get("version", "unknown"),
                manifest_changes=manifest_changes,
                added_files=added,
                removed_files=removed,
                modified_files=modified,
                image_changes=image_changes,
            )

    def _read_manifest(self, zf) -> Dict:
        try:
            return json.loads(zf.read("manifest.json"))
        except Exception:
            return {}

    def _diff_manifests(self, old: Dict, new: Dict) -> Dict[str, Tuple[Any, Any]]:
        changes = {}
        # Check keys in both or either
        all_keys = set(old.keys()) | set(new.keys())

        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)

            if old_val != new_val:
                changes[key] = (old_val, new_val)

        return changes

    def _is_text_file(self, filename: str) -> bool:
        return filename.lower().endswith(
            (".js", ".css", ".html", ".json", ".txt", ".md", ".xml")
        )

    def _is_image_file(self, filename: str) -> bool:
        return filename.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico")
        )

    def _compare_text_ignore_whitespace(self, old: str, new: str) -> bool:
        """Returns True if texts are identical ignoring whitespace."""
        return "".join(old.split()) == "".join(new.split())

    def _compare_js_ast(self, old: str, new: str) -> bool:
        """Returns True if JS code is semantically identical (ignoring comments/formatting)."""
        opts = jsbeautifier.default_options()
        opts.indent_size = 2

        # Beautify both
        old_beautified = jsbeautifier.beautify(old, opts)
        new_beautified = jsbeautifier.beautify(new, opts)

        # Strip comments (simple regex approach)
        def strip_comments(text):
            # Remove single line comments
            text = re.sub(r"//.*", "", text)
            # Remove multi-line comments
            text = re.sub(r"/\*[\s\S]*?\*/", "", text)
            # Remove empty lines
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)

        old_clean = strip_comments(old_beautified)
        new_clean = strip_comments(new_beautified)

        return old_clean == new_clean

    def _compare_images(
        self, old_bytes: bytes, new_bytes: bytes
    ) -> Optional[Dict[str, Any]]:
        """Compare two images and return differences."""
        try:
            old_img = Image.open(io.BytesIO(old_bytes))
            new_img = Image.open(io.BytesIO(new_bytes))

            diff = {}
            if old_img.size != new_img.size:
                diff["size"] = f"{old_img.size} -> {new_img.size}"

            if old_img.mode != new_img.mode:
                diff["mode"] = f"{old_img.mode} -> {new_img.mode}"

            if old_img.format != new_img.format:
                diff["format"] = f"{old_img.format} -> {new_img.format}"

            return diff if diff else None
        except Exception:
            return None
