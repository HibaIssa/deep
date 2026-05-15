from app.services.classification import predict_job_role
from app.services.gap_detection import detect_skill_gaps, get_available_roles
from app.services.llm_gap_refinement import refine_gap_analysis_with_llm
from app.services.llm_recommendation import generate_recommendations
from app.services.preprocessing import preprocess_resume_text
from app.services.resume_parser import extract_resume_text
from app.services.skill_extraction import extract_skills
from app.utils.text_utils import preview_text


MIN_RELIABLE_ROLE_CONFIDENCE = 0.5
MIN_RELIABLE_ROLE_COVERAGE = 15.0
MIN_RELIABLE_ROLE_MATCHES = 2


def build_resume_report(file_path, selected_role: str | None = None) -> dict:
    raw_text = extract_resume_text(file_path)
    preprocessing = preprocess_resume_text(raw_text)
    predicted_role = predict_job_role(preprocessing.processed_text)
    extracted_skills = extract_skills(preprocessing.processed_text, raw_text)
    predicted_role_evidence = _analyze_predicted_role_evidence(
        predicted_role, extracted_skills, raw_text)
    predicted_role = _flag_low_evidence_prediction(
        predicted_role, predicted_role_evidence)
    target_role = _resolve_target_role(selected_role, predicted_role)
    gap_analysis = detect_skill_gaps(extracted_skills, target_role, raw_text)
    raw_text_preview = preview_text(raw_text, 900)
    gap_analysis = refine_gap_analysis_with_llm(
        gap_analysis,
        extracted_skills,
        predicted_role=predicted_role,
        resume_preview=raw_text_preview,
    )
    recommendations = generate_recommendations(
        gap_analysis["target_role"],
        gap_analysis["missing_skills"],
        gap_analysis["matched_skills"],
        predicted_role=predicted_role,
        gap_analysis=gap_analysis,
        resume_preview=raw_text_preview,
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
        "raw_text_preview": raw_text_preview,
    }


def _resolve_target_role(selected_role: str | None, predicted_role: dict) -> str:
    available_roles = get_available_roles()
    if selected_role in available_roles:
        return selected_role

    model_role = predicted_role.get("role")
    if model_role in available_roles:
        return model_role

    return available_roles[0]


def _analyze_predicted_role_evidence(
    predicted_role: dict,
    extracted_skills: list[dict],
    raw_text: str,
) -> dict:
    role = predicted_role.get("role")
    if role not in get_available_roles():
        return {
            "matched_count": 0,
            "coverage_percent": 0.0,
        }

    gap_analysis = detect_skill_gaps(extracted_skills, role, raw_text)
    return {
        "matched_count": len(gap_analysis["matched_skills"]),
        "coverage_percent": gap_analysis["coverage_percent"],
    }


def _flag_low_evidence_prediction(predicted_role: dict, role_evidence: dict) -> dict:
    if predicted_role.get("role") == "Unknown":
        return predicted_role

    confidence = float(predicted_role.get("confidence", 0.0))
    coverage = float(role_evidence.get("coverage_percent", 0.0))
    matched_count = int(role_evidence.get("matched_count", 0))
    if (
        confidence >= MIN_RELIABLE_ROLE_CONFIDENCE
        and coverage >= MIN_RELIABLE_ROLE_COVERAGE
        and matched_count >= MIN_RELIABLE_ROLE_MATCHES
    ):
        return predicted_role

    flagged_prediction = dict(predicted_role)
    flagged_prediction["raw_role"] = predicted_role.get("role")
    flagged_prediction["raw_confidence"] = predicted_role.get("confidence")
    flagged_prediction["role"] = "Cannot decide"
    flagged_prediction["confidence"] = 0.0
    flagged_prediction["warning"] = (
        "The predicted role is not supported by enough resume evidence, so the model cannot make a reliable tech-role prediction."
    )
    flagged_prediction["low_evidence"] = True
    flagged_prediction["evidence_adjusted_confidence"] = 0.0
    flagged_prediction["role_evidence"] = role_evidence
    flagged_prediction["confidence_note"] = (
        " "
    )
    return flagged_prediction
