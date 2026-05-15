import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status

from app.config import ALLOWED_EXTENSIONS, UPLOAD_DIR


def validate_resume_file(filename: str | None) -> None:
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing resume filename.")

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {allowed}.",
        )


def save_upload_file(filename: str, content: bytes) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    extension = Path(filename).suffix.lower()
    safe_stem = _safe_filename(Path(filename).stem)
    saved_name = f"{safe_stem}-{uuid4().hex[:10]}{extension}"
    saved_path = UPLOAD_DIR / saved_name
    saved_path.write_bytes(content)
    return saved_path


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    return cleaned or "resume"
