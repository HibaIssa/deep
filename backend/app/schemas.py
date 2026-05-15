from pydantic import BaseModel, Field


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
    match_evidence: list[dict] = Field(default_factory=list)
    partial_matches: list[dict] = Field(default_factory=list)
    priority_gaps: list[dict] = Field(default_factory=list)
    readiness_level: str = "early"
    waived_skills: list[dict] = Field(default_factory=list)


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
