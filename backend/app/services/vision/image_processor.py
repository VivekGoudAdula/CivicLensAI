"""Image validation and compression before Gemini Vision analysis."""

from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

SUPPORTED_MIME_TYPES: frozenset[str] = frozenset(
    {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }
)

MIME_TO_FORMAT: dict[str, str] = {
    "image/jpeg": "JPEG",
    "image/jpg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}


class ImageProcessingError(ValueError):
    """Raised when an image cannot be processed for vision analysis."""


@dataclass(frozen=True)
class ProcessedImage:
    """Compressed image payload ready for Gemini Vision."""

    data_base64: str
    mime_type: str
    original_width: int
    original_height: int
    output_width: int
    output_height: int
    was_compressed: bool


def normalize_mime_type(mime_type: str | None) -> str:
    """Normalize and validate supported image MIME types."""
    if not mime_type:
        raise ImageProcessingError("Image MIME type is required")
    normalized = mime_type.strip().lower()
    if normalized == "image/jpg":
        normalized = "image/jpeg"
    if normalized not in {"image/jpeg", "image/png", "image/webp"}:
        raise ImageProcessingError(
            f"Unsupported image format: {mime_type}. Supported: JPG, JPEG, PNG, WEBP"
        )
    return normalized


def compress_image_base64(
    image_base64: str,
    mime_type: str,
    *,
    max_dimension: int = 1600,
    jpeg_quality: int = 85,
) -> ProcessedImage:
    """
    Decode, validate, and compress a civic complaint image for Gemini Vision.

    Large images are downscaled preserving aspect ratio. JPEG/WebP use quality
    compression; PNG is optimized when resized.
    """
    normalized_mime = normalize_mime_type(mime_type)
    try:
        raw_bytes = base64.b64decode(image_base64, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ImageProcessingError("Invalid base64 image data") from exc

    if not raw_bytes:
        raise ImageProcessingError("Empty image data")

    try:
        with Image.open(io.BytesIO(raw_bytes)) as image:
            image.load()
            original_width, original_height = image.size
            working = image.convert("RGB") if image.mode not in ("RGB", "L") else image.copy()

            output_width, output_height = original_width, original_height
            was_compressed = False

            longest_side = max(original_width, original_height)
            if longest_side > max_dimension:
                scale = max_dimension / longest_side
                output_width = max(1, int(original_width * scale))
                output_height = max(1, int(original_height * scale))
                working = working.resize((output_width, output_height), Image.Resampling.LANCZOS)
                was_compressed = True

            output_mime = normalized_mime
            buffer = io.BytesIO()

            if normalized_mime in {"image/jpeg", "image/jpg"}:
                working.save(buffer, format="JPEG", quality=jpeg_quality, optimize=True)
                output_mime = "image/jpeg"
                was_compressed = True
            elif normalized_mime == "image/webp":
                working.save(buffer, format="WEBP", quality=jpeg_quality, method=4)
                was_compressed = True
            else:
                if was_compressed or len(raw_bytes) > 1_500_000:
                    working.save(buffer, format="PNG", optimize=True)
                    was_compressed = True
                else:
                    return ProcessedImage(
                        data_base64=image_base64,
                        mime_type=normalized_mime,
                        original_width=original_width,
                        original_height=original_height,
                        output_width=original_width,
                        output_height=original_height,
                        was_compressed=False,
                    )

            compressed_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
            logger.debug(
                "Image compressed %sx%s -> %sx%s (%s, compressed=%s)",
                original_width,
                original_height,
                output_width,
                output_height,
                output_mime,
                was_compressed,
            )
            return ProcessedImage(
                data_base64=compressed_b64,
                mime_type=output_mime,
                original_width=original_width,
                original_height=original_height,
                output_width=output_width,
                output_height=output_height,
                was_compressed=was_compressed,
            )
    except UnidentifiedImageError as exc:
        raise ImageProcessingError("Unrecognized or corrupt image file") from exc
    except OSError as exc:
        raise ImageProcessingError(f"Image processing failed: {exc}") from exc
