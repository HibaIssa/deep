from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.resume_routes import router as resume_router
from app.routes.report_routes import router as report_router


app = FastAPI(
    title="Resume Career Advisor API",
    description="Resume upload, preprocessing, classification, and recommendation API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api/resume", tags=["resume"])
app.include_router(report_router, prefix="/api/report", tags=["report"])


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Resume Career Advisor API is running"}
