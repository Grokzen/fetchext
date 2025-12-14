import logging
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


def optimize_image(path: Path, quality: int = 85) -> Tuple[bool, int, int]:
    """
    Optimize a single image file.

    Args:
        path: Path to the image file.
        quality: Quality setting for optimization (1-100).

    Returns:
        Tuple containing:
        - bool: True if optimization was successful and size was reduced.
        - int: Original file size in bytes.
        - int: New file size in bytes.
    """
    try:
        from PIL import Image

        original_size = path.stat().st_size

        # Open image
        with Image.open(path) as img:
            # Convert to RGB if necessary (e.g. for PNG to JPG conversion, though we keep format here)
            # For now, we just re-save in the same format with optimization

            # Determine format from extension if not available
            fmt = img.format
            if not fmt:
                suffix = path.suffix.lower()
                if suffix in [".jpg", ".jpeg"]:
                    fmt = "JPEG"
                elif suffix == ".png":
                    fmt = "PNG"
                else:
                    return False, original_size, original_size

            # Save to a temporary buffer or file to check size
            # We'll overwrite directly for this tool as per requirements,
            # but let's be safe and save to a temp path first
            temp_path = path.with_suffix(path.suffix + ".tmp")

            save_kwargs = {"optimize": True}
            if fmt == "JPEG":
                save_kwargs["quality"] = quality

            img.save(temp_path, format=fmt, **save_kwargs)

            new_size = temp_path.stat().st_size

            if new_size < original_size:
                temp_path.replace(path)
                logger.debug(
                    f"Optimized {path.name}: {original_size} -> {new_size} bytes"
                )
                return True, original_size, new_size
            else:
                # If no saving, remove temp file
                temp_path.unlink()
                logger.debug(f"Skipped {path.name}: No size reduction")
                return False, original_size, original_size

    except Exception as e:
        logger.error(f"Failed to optimize {path}: {e}")
        return False, 0, 0


def optimize_extension(directory: Path, quality: int = 85) -> Dict[str, any]:
    """
    Optimize all images in an extension directory.

    Args:
        directory: Path to the extension directory (unpacked).
        quality: Quality setting for optimization.

    Returns:
        Dict containing statistics about the optimization run.
    """
    stats = {
        "total_files": 0,
        "optimized_files": 0,
        "original_size": 0,
        "new_size": 0,
        "saved_bytes": 0,
    }

    if not directory.exists() or not directory.is_dir():
        logger.error(f"Directory not found: {directory}")
        return stats

    image_extensions = {".png", ".jpg", ".jpeg"}

    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            stats["total_files"] += 1
            success, orig, new = optimize_image(file_path, quality)

            stats["original_size"] += orig
            if success:
                stats["optimized_files"] += 1
                stats["new_size"] += new
            else:
                stats["new_size"] += orig

    stats["saved_bytes"] = stats["original_size"] - stats["new_size"]
    return stats
