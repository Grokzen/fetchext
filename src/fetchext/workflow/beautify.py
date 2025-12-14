import jsbeautifier
from pathlib import Path
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


class CodeBeautifier:
    def __init__(self):
        self.opts = jsbeautifier.default_options()
        self.opts.indent_size = 2
        self.opts.space_in_empty_paren = True

    def beautify_file(
        self,
        file_path: Union[str, Path],
        in_place: bool = False,
        output_path: Optional[Path] = None,
    ) -> Optional[str]:
        """
        Beautify a JavaScript or JSON file.

        Args:
            file_path: Path to the file to beautify.
            in_place: If True, overwrite the file with formatted content.
            output_path: If provided, write formatted content to this path.

        Returns:
            The formatted code as a string if neither in_place nor output_path is set.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            content = path.read_text(encoding="utf-8")
            formatted = jsbeautifier.beautify(content, self.opts)

            if in_place:
                path.write_text(formatted, encoding="utf-8")
                logger.info(f"Beautified {path} (in-place)")
                return None
            elif output_path:
                out = Path(output_path)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(formatted, encoding="utf-8")
                logger.info(f"Beautified {path} -> {out}")
                return None
            else:
                return formatted
        except Exception as e:
            logger.error(f"Failed to beautify {path}: {e}")
            raise

    def beautify_directory(
        self, dir_path: Union[str, Path], in_place: bool = True
    ) -> None:
        """
        Recursively beautify all JS and JSON files in a directory.

        Args:
            dir_path: Directory to scan.
            in_place: Must be True for directory scanning (simplification).
        """
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            raise NotADirectoryError(f"Directory not found: {path}")

        extensions = ["*.js", "*.json"]
        files = []
        for ext in extensions:
            files.extend(path.rglob(ext))

        for file in files:
            try:
                self.beautify_file(file, in_place=True)
            except Exception as e:
                logger.warning(f"Skipping {file}: {e}")
