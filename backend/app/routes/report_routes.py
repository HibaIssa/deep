from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.config import MAX_UPLOAD_SIZE_BYTES
from app.schemas import ResumeReport
from app.services.gap_detection import get_available_roles
from app.services.report_builder import build_resume_report
from app.utils.file_utils import save_upload_file, validate_resume_file

router = APIRouter()


@router.get("/health")
def report_health():
    return {"status": "ok", "message": "Report generation is available."}


@router.get("/roles")
def list_roles():
    return {"roles": get_available_roles()}


@router.post("/generate", response_model=ResumeReport)
async def generate_report(file: UploadFile = File(...), selected_role: str | None = Form(default=None)):
    validate_resume_file(file.filename)

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume file is too large. Maximum allowed size is 5 MB.",
        )

    saved_path = save_upload_file(file.filename, content)
    return build_resume_report(saved_path, selected_role)
