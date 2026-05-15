from app.services.classification import predict_job_role
from app.services.gap_detection import detect_skill_gaps, get_available_roles
from app.services.llm_recommendation import generate_recommendations
from app.services.preprocessing import preprocess_resume_text
from app.services.resume_parser import extract_resume_text
from app.services.skill_extraction import extract_skills
from app.utils.text_utils import preview_text


def build_resume_report(file_path, selected_role: str | None = None) -> dict:
    raw_text = extract_resume_text(file_path)
    preprocessing = preprocess_resume_text(raw_text)
    predicted_role = predict_job_role(preprocessing.processed_text)
    target_role = _resolve_target_role(selected_role, predicted_role)
    extracted_skills = extract_skills(preprocessing.processed_text, raw_text)
    gap_analysis = detect_skill_gaps(extracted_skills, target_role)
    recommendations = generate_recommendations(
        gap_analysis["target_role"],
        gap_analysis["missing_skills"],
        gap_analysis["matched_skills"],
    )

    return {
        "filename": file_path.name,
        "predicted_role": predicted_role,
        "selected_role": gap_analysis["target_role"],
        "extracted_skills": extracted_skills,
        "gap_analysis": gap_analysis,
        "recommendations": recommendations,
        "preprocessing": {
            "processed_text": preprocessing.processed_text,
            "tokens": preprocessing.tokens,
            "stats": preprocessing.stats,
        },
        "raw_text_preview": preview_text(raw_text, 900),
    }


def _resolve_target_role(selected_role: str | None, predicted_role: dict) -> str:
    available_roles = get_available_roles()
    if selected_role in available_roles:
        return selected_role

    model_role = predicted_role.get("role")
    if model_role in available_roles:
        return model_role

    return available_roles[0]
