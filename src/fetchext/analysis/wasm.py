import struct
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class WasmAnalyzer:
    """
    Analyzes WebAssembly (.wasm) files.
    """

    SECTION_NAMES = {
        0: "Custom",
        1: "Type",
        2: "Import",
        3: "Function",
        4: "Table",
        5: "Memory",
        6: "Global",
        7: "Export",
        8: "Start",
        9: "Element",
        10: "Code",
        11: "Data",
        12: "DataCount",
    }

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = b""
        self.pos = 0

    def analyze(self) -> Dict[str, Any]:
        """
        Perform analysis on the WASM file.
        """
        try:
            with open(self.file_path, "rb") as f:
                self.content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {self.file_path}: {e}")
            return {"error": str(e)}

        if len(self.content) < 8:
            return {"error": "File too small to be WASM"}

        # Check Magic and Version
        magic = self.content[0:4]
        version = self.content[4:8]

        if magic != b"\x00asm":
            return {"error": "Invalid WASM magic number"}

        version_int = struct.unpack("<I", version)[0]

        stats = {
            "size": len(self.content),
            "version": version_int,
            "sections": [],
            "imports": [],
            "exports": [],
            "functions_count": 0,
            "custom_sections": [],
        }

        self.pos = 8
        while self.pos < len(self.content):
            try:
                section_id = self._read_byte()
                section_size = self._read_leb128()

                section_name = self.SECTION_NAMES.get(
                    section_id, f"Unknown({section_id})"
                )
                section_start = self.pos

                stats["sections"].append(
                    {"id": section_id, "name": section_name, "size": section_size}
                )

                if section_id == 2:  # Import Section
                    self._parse_import_section(section_start, section_size, stats)
                elif section_id == 7:  # Export Section
                    self._parse_export_section(section_start, section_size, stats)
                elif section_id == 3:  # Function Section
                    # Just count them for now, parsing types is complex
                    count = self._read_leb128()
                    stats["functions_count"] = count
                elif section_id == 0:  # Custom Section
                    name = self._parse_custom_section_name(section_start, section_size)
                    stats["custom_sections"].append(name)

                # Skip to next section
                self.pos = section_start + section_size

            except IndexError:
                break
            except Exception as e:
                logger.warning(f"Error parsing section at {self.pos}: {e}")
                break

        return stats

    def _read_byte(self) -> int:
        if self.pos >= len(self.content):
            raise IndexError("End of file")
        b = self.content[self.pos]
        self.pos += 1
        return b

    def _read_leb128(self) -> int:
        result = 0
        shift = 0
        while True:
            byte = self._read_byte()
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result

    def _read_string(self) -> str:
        length = self._read_leb128()
        bytes_str = self.content[self.pos : self.pos + length]
        self.pos += length
        return bytes_str.decode("utf-8", errors="replace")

    def _parse_import_section(self, start: int, size: int, stats: Dict):
        # Save current pos
        original_pos = self.pos

        try:
            count = self._read_leb128()
            for _ in range(count):
                module = self._read_string()
                field = self._read_string()
                kind = self._read_byte()

                # Skip type description based on kind
                if kind == 0:  # Function
                    self._read_leb128()  # Type index
                elif kind == 1:  # Table
                    self._read_byte()  # elem_type
                    self._read_limits()
                elif kind == 2:  # Memory
                    self._read_limits()
                elif kind == 3:  # Global
                    self._read_byte()  # content_type
                    self._read_byte()  # mutability

                stats["imports"].append(
                    {"module": module, "field": field, "kind": kind}
                )
        except Exception as e:
            logger.warning(f"Failed to parse import section: {e}")
        finally:
            # Restore pos to ensure we skip correctly in main loop
            self.pos = original_pos

    def _parse_export_section(self, start: int, size: int, stats: Dict):
        original_pos = self.pos
        try:
            count = self._read_leb128()
            for _ in range(count):
                name = self._read_string()
                kind = self._read_byte()
                index = self._read_leb128()

                stats["exports"].append({"name": name, "kind": kind, "index": index})
        except Exception as e:
            logger.warning(f"Failed to parse export section: {e}")
        finally:
            self.pos = original_pos

    def _parse_custom_section_name(self, start: int, size: int) -> str:
        original_pos = self.pos
        try:
            name = self._read_string()
            return name
        except Exception:
            return "unknown"
        finally:
            self.pos = original_pos

    def _read_limits(self):
        flags = self._read_byte()
        self._read_leb128()  # min
        if flags & 1:
            self._read_leb128()  # max


def analyze_wasm(file_path: Path) -> Dict[str, Any]:
    """
    Analyze a WASM file and return statistics.
    """
    analyzer = WasmAnalyzer(file_path)
    return analyzer.analyze()
