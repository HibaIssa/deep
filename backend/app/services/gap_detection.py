import json
import math
from collections import Counter

from app.config import DATA_DIR
from app.services.skill_extraction import SKILL_ALIASES, _contains_phrase, _tokens


MIN_TFIDF_MATCH_SCORE = 0.6
MIN_EXTRACTED_TFIDF_SCORE = 0.5


def detect_skill_gaps(
    extracted_skills: list[dict],
    target_role: str,
    resume_text: str = "",
) -> dict:
    ontology = _load_skill_ontology()
    if target_role not in ontology:
        target_role = _default_role(ontology)

    required_skills = ontology[target_role]
    match_evidence = _build_match_evidence(required_skills, extracted_skills, resume_text)
    matched_skills = [skill for skill in required_skills if skill.lower() in match_evidence]

    matched_names = {skill.lower() for skill in matched_skills}
    missing_skills = [skill for skill in required_skills if skill.lower() not in matched_names]
    coverage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0

    return {
        "target_role": target_role,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "coverage_percent": round(coverage, 1),
        "match_evidence": [match_evidence[skill.lower()] for skill in matched_skills],
    }


def get_available_roles() -> list[str]:
    return list(_load_skill_ontology().keys())


def _load_skill_ontology() -> dict[str, list[str]]:
    return json.loads((DATA_DIR / "skills_ontology.json").read_text(encoding="utf-8"))


def _default_role(ontology: dict[str, list[str]]) -> str:
    return next(iter(ontology.keys()))


def _match_required_skills_from_extracted(
    required_skills: list[str],
    extracted_skills: list[dict],
) -> list[str]:
    extracted_names = {item["skill"].lower() for item in extracted_skills}
    return [skill for skill in required_skills if skill.lower() in extracted_names]


def _build_match_evidence(
    required_skills: list[str],
    extracted_skills: list[dict],
    resume_text: str,
) -> dict[str, dict]:
    required_lookup = {skill.lower(): skill for skill in required_skills}
    evidence: dict[str, dict] = {}

    for item in extracted_skills:
        skill_name = str(item.get("skill", "")).lower()
        if skill_name not in required_lookup or not _is_confident_extracted_match(item):
            continue

        canonical_skill = required_lookup[skill_name]
        evidence[skill_name] = {
            "skill": canonical_skill,
            "source": item.get("source", "extracted"),
            "score": float(item.get("score", 1.0)),
            "matched_alias": None,
        }

    if resume_text.strip():
        _add_phrase_match_evidence(required_skills, resume_text, evidence)
        _add_single_token_tfidf_evidence(required_skills, resume_text, evidence)

    return evidence


def _is_confident_extracted_match(item: dict) -> bool:
    source = item.get("source")
    if source in {"keyword", "semantic"}:
        return True
    if source == "tf-idf":
        skill_name = str(item.get("skill", ""))
        return (
            len(_tokens(skill_name)) == 1
            and float(item.get("score", 0.0)) >= MIN_EXTRACTED_TFIDF_SCORE
        )
    return False


def _add_phrase_match_evidence(
    required_skills: list[str],
    resume_text: str,
    evidence: dict[str, dict],
) -> None:
    searchable_text = resume_text.lower()
    for skill in required_skills:
        skill_key = skill.lower()
        if skill_key in evidence:
            continue

        matched_alias = _find_phrase_or_alias(searchable_text, skill)
        if not matched_alias:
            continue

        evidence[skill_key] = {
            "skill": skill,
            "source": "phrase",
            "score": 1.0,
            "matched_alias": matched_alias,
        }


def _find_phrase_or_alias(searchable_text: str, skill: str) -> str | None:
    for phrase in sorted(_skill_phrases(skill), key=lambda item: (-len(item), item)):
        if _contains_phrase(searchable_text, phrase):
            return phrase
    return None


def _add_single_token_tfidf_evidence(
    required_skills: list[str],
    resume_text: str,
    evidence: dict[str, dict],
) -> None:
    single_token_skills = [skill for skill in required_skills if len(_tokens(skill)) == 1]
    for skill in _match_required_skills_with_tfidf(single_token_skills, resume_text):
        skill_key = skill.lower()
        if skill_key in evidence:
            continue
        evidence[skill_key] = {
            "skill": skill,
            "source": "tf-idf",
            "score": round(_single_skill_tfidf_score(skill, single_token_skills, resume_text), 3),
            "matched_alias": None,
        }


def _match_required_skills_with_tfidf(required_skills: list[str], resume_text: str) -> list[str]:
    token_counts = Counter(_tokens(resume_text))
    keyword_documents = [_skill_keyword_terms(skill) for skill in required_skills]
    matched_skills = []

    for skill in required_skills:
        score = _tf_idf_keyword_score(skill, token_counts, keyword_documents)
        if score >= MIN_TFIDF_MATCH_SCORE:
            matched_skills.append(skill)

    return matched_skills


def _single_skill_tfidf_score(skill: str, required_skills: list[str], resume_text: str) -> float:
    token_counts = Counter(_tokens(resume_text))
    keyword_documents = [_skill_keyword_terms(candidate) for candidate in required_skills]
    return _tf_idf_keyword_score(skill, token_counts, keyword_documents)


def _tf_idf_keyword_score(
    skill: str,
    token_counts: Counter,
    keyword_documents: list[set[str]],
) -> float:
    candidate_phrases = _skill_phrases(skill)
    return max(
        (_phrase_tf_idf_score(phrase, token_counts, keyword_documents) for phrase in candidate_phrases),
        default=0.0,
    )


def _phrase_tf_idf_score(
    phrase: str,
    token_counts: Counter,
    keyword_documents: list[set[str]],
) -> float:
    phrase_terms = _tokens(phrase)
    if not phrase_terms:
        return 0.0

    matched_weight = 0.0
    total_weight = 0.0
    for term in phrase_terms:
        document_frequency = sum(1 for terms in keyword_documents if term in terms)
        idf = math.log((1 + len(keyword_documents)) / (1 + document_frequency)) + 1
        total_weight += idf
        if token_counts[term] > 0:
            matched_weight += (1 + math.log(token_counts[term])) * idf

    if total_weight == 0:
        return 0.0

    return min(matched_weight / total_weight, 1.0)


def _skill_keyword_terms(skill: str) -> set[str]:
    phrases = _skill_phrases(skill)
    return {term for phrase in phrases for term in _tokens(phrase)}


def _skill_phrases(skill: str) -> set[str]:
    return {skill.lower(), *SKILL_ALIASES.get(skill.lower(), set())}
