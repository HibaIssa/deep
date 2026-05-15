from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    username: str


class SkillMatch(BaseModel):
    skill: str
    source: str
    score: float


class GapAnalysis(BaseModel):
    target_role: str
    required_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    coverage_percent: float


class RecommendationItem(BaseModel):
    title: str
    detail: str
    priority: str


class ResumeReport(BaseModel):
    filename: str
    predicted_role: dict
    selected_role: str
    extracted_skills: list[SkillMatch]
    gap_analysis: GapAnalysis
    recommendations: list[RecommendationItem]
    preprocessing: dict
    raw_text_preview: str


class SavedReportCreate(BaseModel):
    title: str
    report: ResumeReport


class SavedReportSummary(BaseModel):
    id: int
    title: str
    selected_role: str
    coverage_percent: float
    created_at: str
