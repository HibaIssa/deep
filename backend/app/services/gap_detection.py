import json

from app.config import DATA_DIR


def detect_skill_gaps(extracted_skills: list[dict], target_role: str) -> dict:
    ontology = _load_skill_ontology()
    if target_role not in ontology:
        target_role = _default_role(ontology)

    required_skills = ontology[target_role]
    extracted_names = {item["skill"].lower() for item in extracted_skills}
    matched_skills = [skill for skill in required_skills if skill.lower() in extracted_names]
    missing_skills = [skill for skill in required_skills if skill.lower() not in extracted_names]
    coverage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0

    return {
        "target_role": target_role,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "coverage_percent": round(coverage, 1),
    }


def get_available_roles() -> list[str]:
    return list(_load_skill_ontology().keys())


def _load_skill_ontology() -> dict[str, list[str]]:
    return json.loads((DATA_DIR / "skills_ontology.json").read_text(encoding="utf-8"))


def _default_role(ontology: dict[str, list[str]]) -> str:
    return next(iter(ontology.keys()))
