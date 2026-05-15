from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.config import MAX_UPLOAD_SIZE_BYTES
from app.schemas import ResumeReport, SavedReportCreate, SavedReportSummary
from app.services import storage
from app.services.auth import get_current_user
from app.services.gap_detection import get_available_roles
from app.services.pdf_export import build_report_pdf
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


@router.post("/export-pdf")
def export_report_pdf(report: ResumeReport):
    pdf_buffer = build_report_pdf(report.model_dump())
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume-career-report.pdf"},
    )


@router.post("/saved", response_model=SavedReportSummary)
def save_current_report(payload: SavedReportCreate, user=Depends(get_current_user)):
    report = payload.report.model_dump()
    report_id = storage.save_report(user["id"], payload.title.strip() or "Resume report", report)
    return {
        "id": report_id,
        "title": payload.title,
        "selected_role": report["selected_role"],
        "coverage_percent": report["gap_analysis"]["coverage_percent"],
        "created_at": storage.utc_now(),
    }


@router.get("/saved", response_model=list[SavedReportSummary])
def list_saved_reports(user=Depends(get_current_user)):
    return storage.list_reports(user["id"])


@router.get("/saved/{report_id}", response_model=ResumeReport)
def get_saved_report(report_id: int, user=Depends(get_current_user)):
    report = storage.get_report(user["id"], report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved report not found.")
    return report


@router.delete("/saved/{report_id}")
def delete_saved_report(report_id: int, user=Depends(get_current_user)):
    deleted = storage.delete_report(user["id"], report_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved report not found.")
    return {"status": "deleted"}
