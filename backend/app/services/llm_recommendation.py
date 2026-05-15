def generate_recommendations(role: str, missing_skills: list[str], matched_skills: list[str]) -> list[dict]:
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
