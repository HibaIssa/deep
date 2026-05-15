from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "data" / "resume_advisor.db"

MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
AUTH_SECRET = os.getenv("AUTH_SECRET", "resume-career-advisor-dev-secret")
