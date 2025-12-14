import logging
import shutil
import zipfile
from pathlib import Path
from .crx import CrxDecoder

logger = logging.getLogger(__name__)


class FormatConverter:
    """
    Converts between extension formats.
    """

    @staticmethod
    def convert_to_zip(input_path: Path, output_path: Path = None):
        """
        Convert a CRX file or Directory to a ZIP file.
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input not found: {input_path}")

        if output_path:
            output_path = Path(output_path)
        else:
            output_path = input_path.with_suffix(".zip")

        if input_path.is_dir():
            FormatConverter._dir_to_zip(input_path, output_path)
        elif input_path.is_file():
            FormatConverter._crx_to_zip(input_path, output_path)
        else:
            raise ValueError("Input must be a file or directory")

        return output_path

    @staticmethod
    def _crx_to_zip(input_path: Path, output_path: Path):
        """
        Extract ZIP payload from CRX.
        """
        offset = CrxDecoder.get_zip_offset(input_path)

        logger.info(f"Converting CRX to ZIP (Offset: {offset})...")

        with input_path.open("rb") as fin:
            fin.seek(offset)
            with output_path.open("wb") as fout:
                shutil.copyfileobj(fin, fout)

        logger.info(f"Saved to {output_path}")

    @staticmethod
    def _dir_to_zip(input_path: Path, output_path: Path):
        """
        Pack directory into ZIP.
        """
        logger.info(f"Packing directory {input_path} to {output_path}...")

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in input_path.rglob("*"):
                if file.is_file():
                    # Archive name should be relative to input_path
                    arcname = file.relative_to(input_path)
                    zf.write(file, arcname)

        logger.info(f"Saved to {output_path}")
