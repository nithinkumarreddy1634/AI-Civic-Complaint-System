"""
Image upload service — validates, processes, and stores uploaded images.

Validation checks:
    1. File extension whitelist (jpg, jpeg, png)
    2. MIME type verification via file header bytes
    3. File size limit
    4. Image integrity (not corrupted) via PIL
    5. Image dimension bounds (min 100x100, max 10000x10000)
    6. UUID-based filename generation for security
"""
import os
import uuid
from fastapi import UploadFile, HTTPException, status
from PIL import Image
from io import BytesIO
from typing import Tuple

# File header signatures for MIME type verification
_MIME_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
}


def _detect_mime_type(content: bytes) -> str | None:
    """Detect MIME type from file header bytes (no external library needed)."""
    for signature, mime_type in _MIME_SIGNATURES.items():
        if content[:len(signature)] == signature:
            return mime_type
    return None


async def validate_and_save_image(file: UploadFile, settings) -> Tuple[str, str]:
    """
    Validate and save an uploaded image file.

    Args:
        file: FastAPI UploadFile from multipart form
        settings: Application settings instance

    Returns:
        Tuple of (saved_file_path, original_filename)

    Raises:
        HTTPException 400: If validation fails (extension, size, MIME, corruption, dimensions)
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    # 1. Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = {f".{e}" for e in settings.allowed_extensions_list}
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}'. Allowed: {', '.join(allowed_exts)}",
        )

    # 2. Read file content and validate size
    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({len(content)} bytes) exceeds maximum ({settings.MAX_FILE_SIZE_MB} MB)",
        )

    # 3. Validate MIME type via file header bytes
    detected_mime = _detect_mime_type(content)
    if detected_mime not in ("image/jpeg", "image/png"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG images are accepted.",
        )

    # 4. Validate image integrity (not corrupted)
    try:
        image = Image.open(BytesIO(content))
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file is corrupted or invalid",
        )

    # 5. Validate image dimensions
    # Re-open because verify() may close or alter internal state
    image = Image.open(BytesIO(content))
    width, height = image.size
    if width < 100 or height < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too small ({width}x{height}). Minimum is 100x100 pixels.",
        )
    if width > 10000 or height > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too large ({width}x{height}). Maximum is 10000x10000 pixels.",
        )

    # 6. Generate secure UUID filename and save
    filename = f"{uuid.uuid4()}{ext}"
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    saved_path = os.path.join(upload_dir, filename)

    with open(saved_path, "wb") as f:
        f.write(content)

    safe_original_name = os.path.basename(file.filename.replace("\\", "/")) or f"image{ext}"
    return saved_path, safe_original_name


def delete_image(image_path: str) -> None:
    """Delete an image file from storage."""
    if os.path.exists(image_path):
        os.remove(image_path)


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """Get (width, height) of an image file."""
    with Image.open(image_path) as img:
        return img.size
