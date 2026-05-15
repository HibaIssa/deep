import json
from urllib import error, request

from app.config import GEMINI_API_BASE_URL, GEMINI_API_KEY, GEMINI_MODEL


GEMINI_TIMEOUT_SECONDS = 20
VALID_PRIORITIES = {"High", "Medium", "Low"}
VALID_STATUSES = {"missing", "partial"}
MAX_REASON_LENGTH = 220


def refine_gap_analysis_with_llm(
    gap_analysis: dict,
    extracted_skills: list[dict],
    predicted_role: dict | None = None,
    resume_preview: str = "",
) -> dict:
    if not GEMINI_API_KEY:
        return gap_analysis

    try:
        refined = _generate_gap_refinement(
            gap_analysis=gap_analysis,
            extracted_skills=extracted_skills,
            predicted_role=predicted_role or {},
            resume_preview=resume_preview,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return gap_analysis

    return _merge_refinement(gap_analysis, refined)


def _generate_gap_refinement(
    gap_analysis: dict,
    extracted_skills: list[dict],
    predicted_role: dict,
    resume_preview: str,
) -> dict:
    prompt_data = {
        "predicted_role": predicted_role,
        "target_role": gap_analysis.get("target_role"),
        "coverage_percent": gap_analysis.get("coverage_percent"),
        "readiness_level": gap_analysis.get("readiness_level"),
        "required_skills": gap_analysis.get("required_skills", []),
        "matched_skills": gap_analysis.get("matched_skills", []),
        "missing_skills": gap_analysis.get("missing_skills", []),
        "priority_gaps": gap_analysis.get("priority_gaps", []),
        "partial_matches": gap_analysis.get("partial_matches", []),
        "match_evidence": gap_analysis.get("match_evidence", []),
        "waived_skills": gap_analysis.get("waived_skills", []),
        "extracted_skills": extracted_skills[:40],
        "resume_preview": resume_preview[:900],
    }
    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": (
                        "You are a strict resume skill-gap reviewer. Refine prioritization and "
                        "explain the deterministic gap analysis using only the supplied data. "
                        "Do not add new required skills, matched skills, missing skills, credentials, "
                        "or experience. Return JSON only."
                    )
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Review this gap analysis. Return JSON with two keys: "
                            "'priority_gaps' and 'insights'. "
                            "'priority_gaps' must contain only skills already present in the provided "
                            "priority_gaps list, each with skill, priority, status, and a short reason. "
                            "'insights' must contain 1 to 3 concise observations with title, detail, "
                            "and priority. Prioritize core role gaps, partial transferable evidence, "
                            "and the selected target role.\n\n"
                            f"{json.dumps(prompt_data, ensure_ascii=False)}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    response_data = _post_gemini(payload)
    response_text = _extract_response_text(response_data)
    return _validate_refinement(json.loads(response_text), gap_analysis)


def _post_gemini(payload: dict) -> dict:
    url = f"{GEMINI_API_BASE_URL}/models/{GEMINI_MODEL}:generateContent"
    body = json.dumps(payload).encode("utf-8")
    api_request = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        },
        method="POST",
    )
    try:
        with request.urlopen(api_request, timeout=GEMINI_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Gemini gap-refinement request failed: {detail}") from exc


def _extract_response_text(response_data: dict) -> str:
    candidates = response_data.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini returned no candidates")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise ValueError("Gemini returned an empty response")
    return text


def _validate_refinement(parsed: object, gap_analysis: dict) -> dict:
    if not isinstance(parsed, dict):
        raise ValueError("Gemini gap refinement must be an object")

    allowed_gaps = {
        str(item.get("skill", "")).lower(): item
        for item in gap_analysis.get("priority_gaps", [])
        if isinstance(item, dict)
    }
    priority_gaps = _validate_priority_gaps(parsed.get("priority_gaps"), allowed_gaps)
    insights = _validate_insights(parsed.get("insights"))

    if not priority_gaps and not insights:
        raise ValueError("Gemini returned no usable gap refinement")

    return {
        "priority_gaps": priority_gaps,
        "insights": insights,
    }


def _validate_priority_gaps(items: object, allowed_gaps: dict[str, dict]) -> list[dict]:
    if not isinstance(items, list):
        return []

    priority_gaps = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            continue

        skill = str(item.get("skill", "")).strip()
        skill_key = skill.lower()
        if not skill or skill_key in seen or skill_key not in allowed_gaps:
            continue

        original_gap = allowed_gaps[skill_key]
        priority = str(item.get("priority", original_gap.get("priority", "Medium"))).strip().title()
        status = str(item.get("status", original_gap.get("status", "missing"))).strip().lower()
        reason = str(item.get("reason", "")).strip()

        if priority not in VALID_PRIORITIES:
            priority = original_gap.get("priority", "Medium")
        if status not in VALID_STATUSES:
            status = original_gap.get("status", "missing")

        priority_gaps.append(
            {
                "skill": original_gap.get("skill", skill),
                "priority": priority,
                "status": status,
                "reason": reason[:MAX_REASON_LENGTH],
            }
        )
        seen.add(skill_key)

    return priority_gaps


def _validate_insights(items: object) -> list[dict]:
    if not isinstance(items, list):
        return []

    insights = []
    for item in items[:3]:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()
        detail = str(item.get("detail", "")).strip()
        priority = str(item.get("priority", "Medium")).strip().title()
        if not title or not detail:
            continue
        if priority not in VALID_PRIORITIES:
            priority = "Medium"

        insights.append(
            {
                "title": title[:90],
                "detail": detail[:260],
                "priority": priority,
            }
        )

    return insights


def _merge_refinement(gap_analysis: dict, refined: dict) -> dict:
    merged = dict(gap_analysis)
    if refined["priority_gaps"]:
        merged["priority_gaps"] = _complete_priority_gaps(
            refined["priority_gaps"],
            gap_analysis.get("priority_gaps", []),
        )
        merged["missing_skills"] = _reorder_missing_skills(
            gap_analysis.get("missing_skills", []),
            merged["priority_gaps"],
        )

    merged["llm_refinement"] = {
        "enabled": True,
        "model": GEMINI_MODEL,
        "insights": refined["insights"],
    }
    return merged


def _complete_priority_gaps(refined_gaps: list[dict], original_gaps: list[dict]) -> list[dict]:
    refined_names = {item["skill"].lower() for item in refined_gaps}
    remaining_gaps = [
        item
        for item in original_gaps
        if isinstance(item, dict) and str(item.get("skill", "")).lower() not in refined_names
    ]
    return [*refined_gaps, *remaining_gaps]


def _reorder_missing_skills(missing_skills: list[str], priority_gaps: list[dict]) -> list[str]:
    missing_lookup = {skill.lower(): skill for skill in missing_skills}
    ordered = [
        missing_lookup[item["skill"].lower()]
        for item in priority_gaps
        if item.get("status") == "missing" and item["skill"].lower() in missing_lookup
    ]
    ordered_names = {skill.lower() for skill in ordered}
    return [*ordered, *[skill for skill in missing_skills if skill.lower() not in ordered_names]]
