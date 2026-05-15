import json
import math
import re
from collections import Counter
from pathlib import Path

from app.config import DATA_DIR


SKILL_ALIASES = {
    "javascript": {"js", "javascript"},
    "typescript": {"ts", "typescript"},
    "react": {"react", "react.js", "reactjs"},
    "fastapi": {"fastapi", "fast api"},
    "sql": {"sql", "postgres", "postgresql", "mysql", "sqlite"},
    "python": {"python", "py"},
    "machine learning": {"machine learning", "ml"},
    "data visualization": {"data visualization", "dashboarding", "tableau", "power bi"},
    "databases": {"database", "databases", "dbms"},
    "api design": {"api design", "rest api", "restful api"},
    "testing": {"testing", "unit testing", "pytest", "jest"},
    "git": {"git", "github", "gitlab"},
}


def extract_skills(processed_text: str, raw_text: str = "") -> list[dict]:
    ontology_skills = _load_ontology_skills()
    searchable_text = f"{processed_text} {raw_text}".lower()
    tokens = _tokens(searchable_text)
    token_counts = Counter(tokens)
    results: dict[str, dict] = {}

    for skill in ontology_skills:
        aliases = SKILL_ALIASES.get(skill, {skill})
        for alias in aliases:
            if _contains_phrase(searchable_text, alias):
                results[skill] = {
                    "skill": skill,
                    "source": "keyword",
                    "score": 1.0,
                }
                break

    for skill in ontology_skills:
        if skill in results:
            continue
        score = _tf_idf_like_score(skill, token_counts, ontology_skills)
        if score >= 0.18:
            results[skill] = {
                "skill": skill,
                "source": "tf-idf",
                "score": round(score, 3),
            }

    for skill in ontology_skills:
        if skill in results:
            continue
        semantic_score = _semantic_overlap(skill, tokens)
        if semantic_score >= 0.72:
            results[skill] = {
                "skill": skill,
                "source": "semantic",
                "score": round(semantic_score, 3),
            }

    return sorted(results.values(), key=lambda item: (-item["score"], item["skill"]))


def _load_ontology_skills() -> list[str]:
    data = json.loads((DATA_DIR / "skills_ontology.json").read_text(encoding="utf-8"))
    skills = {skill.lower() for role_skills in data.values() for skill in role_skills}
    return sorted(skills)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#.]+(?:-[a-z0-9+#.]+)?", text.lower())


def _contains_phrase(text: str, phrase: str) -> bool:
    escaped = re.escape(phrase.lower())
    return re.search(rf"(?<![a-z0-9+#.]){escaped}(?![a-z0-9+#.])", text) is not None


def _tf_idf_like_score(skill: str, token_counts: Counter, all_skills: list[str]) -> float:
    skill_terms = _tokens(skill)
    if not skill_terms:
        return 0.0

    total_tokens = max(sum(token_counts.values()), 1)
    score = 0.0
    for term in skill_terms:
        tf = token_counts[term] / total_tokens
        document_frequency = sum(1 for candidate in all_skills if term in _tokens(candidate))
        idf = math.log((1 + len(all_skills)) / (1 + document_frequency)) + 1
        score += tf * idf * 10
    return score / len(skill_terms)


def _semantic_overlap(skill: str, tokens: list[str]) -> float:
    skill_terms = set(_tokens(skill))
    token_set = set(tokens)
    if not skill_terms:
        return 0.0
    direct_overlap = len(skill_terms & token_set) / len(skill_terms)
    alias_overlap = 0.0
    for alias in SKILL_ALIASES.get(skill, set()):
        alias_terms = set(_tokens(alias))
        if alias_terms:
            alias_overlap = max(alias_overlap, len(alias_terms & token_set) / len(alias_terms))
    return max(direct_overlap, alias_overlap)
