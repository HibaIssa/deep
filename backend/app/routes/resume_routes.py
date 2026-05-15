from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import MAX_UPLOAD_SIZE_BYTES
from app.services.preprocessing import preprocess_resume_text
from app.services.resume_parser import extract_resume_text
from app.utils.file_utils import save_upload_file, validate_resume_file


router = APIRouter()


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    validate_resume_file(file.filename)

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume file is too large. Maximum allowed size is 5 MB.",
        )

    saved_path = save_upload_file(file.filename, content)
    raw_text = extract_resume_text(saved_path)
    preprocessing_result = preprocess_resume_text(raw_text)

    return {
        "filename": saved_path.name,
        "raw_text": raw_text,
        "processed_text": preprocessing_result.processed_text,
        "tokens": preprocessing_result.tokens,
        "stats": preprocessing_result.stats,
    }
