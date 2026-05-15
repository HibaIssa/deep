import json
from urllib import error, request

from app.config import GEMINI_API_BASE_URL, GEMINI_API_KEY, GEMINI_MODEL


GEMINI_TIMEOUT_SECONDS = 20
VALID_PRIORITIES = {"High", "Medium", "Low"}


def generate_recommendations(
    role: str,
    missing_skills: list[str],
    matched_skills: list[str],
    predicted_role: dict | None = None,
    gap_analysis: dict | None = None,
    resume_preview: str = "",
) -> list[dict]:
    if GEMINI_API_KEY:
        try:
            return _generate_with_gemini(
                role=role,
                missing_skills=missing_skills,
                matched_skills=matched_skills,
                predicted_role=predicted_role or {},
                gap_analysis=gap_analysis or {},
                resume_preview=resume_preview,
            )
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            pass

    return _generate_fallback_recommendations(role, missing_skills, matched_skills)


def _generate_with_gemini(
    role: str,
    missing_skills: list[str],
    matched_skills: list[str],
    predicted_role: dict,
    gap_analysis: dict,
    resume_preview: str,
) -> list[dict]:
    prompt_data = {
        "predicted_role": predicted_role,
        "target_role": role,
        "coverage_percent": gap_analysis.get("coverage_percent"),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "required_skills": gap_analysis.get("required_skills", []),
        "resume_preview": resume_preview[:900],
    }
    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": (
                        "You are a career advisor for resume improvement. Generate practical, "
                        "evidence-based recommendations from only the provided role classification "
                        "and skill-gap data. Do not invent experience, credentials, or skills. "
                        "Return JSON only."
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
                            "Create 3 to 5 recommendation items for this resume analysis. "
                            "Each item must include title, detail, and priority. Priority must be "
                            "High, Medium, or Low.\n\n"
                            f"{json.dumps(prompt_data, ensure_ascii=False)}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
        },
    }

    response_data = _post_gemini(payload)
    response_text = _extract_response_text(response_data)
    parsed = json.loads(response_text)
    return _validate_recommendations(parsed)


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
        raise ValueError(f"Gemini request failed: {detail}") from exc


def _extract_response_text(response_data: dict) -> str:
    candidates = response_data.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini returned no candidates")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise ValueError("Gemini returned an empty response")
    return text


def _validate_recommendations(parsed: object) -> list[dict]:
    items = parsed.get("recommendations") if isinstance(parsed, dict) else parsed
    if not isinstance(items, list):
        raise ValueError("Gemini recommendations must be a list")

    recommendations: list[dict] = []
    for item in items[:5]:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()
        detail = str(item.get("detail", "")).strip()
        priority = str(item.get("priority", "")).strip().title()
        if not title or not detail:
            continue
        if priority not in VALID_PRIORITIES:
            priority = "Medium"

        recommendations.append(
            {
                "title": title,
                "detail": detail,
                "priority": priority,
            }
        )

    if not recommendations:
        raise ValueError("Gemini returned no valid recommendation items")
    return recommendations


def _generate_fallback_recommendations(
    role: str,
    missing_skills: list[str],
    matched_skills: list[str],
) -> list[dict]:
    recommendations: list[dict] = []

    if missing_skills:
        top_missing = missing_skills[:3]
        recommendations.append(
            {
                "title": "Close the highest-impact skill gaps",
                "detail": (
                    f"For a {role} path, prioritize {', '.join(top_missing)}. Add one focused "
                    "project or course artifact for each skill so the resume shows evidence, not only keywords."
                ),
                "priority": "High",
            }
        )
    else:
        recommendations.append(
            {
                "title": "Strengthen role alignment",
                "detail": (
                    f"Your resume covers the core {role} skill set. Improve it by adding measurable outcomes, "
                    "project scale, and business impact beside the technical skills."
                ),
                "priority": "High",
            }
        )

    if matched_skills:
        recommendations.append(
            {
                "title": "Make existing strengths more visible",
                "detail": (
                    f"The resume already signals {', '.join(matched_skills[:4])}. Move the strongest examples "
                    "into bullet points with action verbs, metrics, and tools used."
                ),
                "priority": "Medium",
            }
        )

    recommendations.append(
        {
            "title": "Add a targeted summary",
            "detail": (
                f"Open the resume with a 2-3 line summary tailored to {role}. Mention the target role, "
                "your strongest relevant tools, and one concrete achievement."
            ),
            "priority": "Medium",
        }
    )

    return recommendations
