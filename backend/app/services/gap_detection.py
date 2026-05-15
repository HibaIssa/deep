import json
import math
from collections import Counter

from app.config import DATA_DIR
from app.services.skill_extraction import SKILL_ALIASES, _contains_phrase, _tokens


MIN_TFIDF_MATCH_SCORE = 0.6
MIN_EXTRACTED_TFIDF_SCORE = 0.5
PARTIAL_MATCH_CREDIT = 0.25


ROLE_ALTERNATIVE_GROUPS = {
    "Backend Developer": [
        {"node.js", "fastapi", "django"},
    ],
    "Full Stack Developer": [
        {"javascript", "typescript"},
    ],
    "Frontend Developer": [
        {"javascript", "typescript"},
    ],
    "Database Engineer": [
        {"postgresql", "mysql"},
    ],
    "DevOps/Cloud Engineer": [
        {"aws", "azure", "gcp", "cloud"},
        {"terraform", "infrastructure as code"},
    ],
    "QA Engineer": [
        {"selenium", "pytest", "jest", "cypress"},
        {"manual testing", "test automation"},
    ],
    "AI/ML Engineer": [
        {"pytorch", "tensorflow"},
        {"model deployment", "mlops"},
    ],
    "Data Engineer": [
        {"cloud", "aws", "azure", "gcp"},
    ],
    "Mobile Developer": [
        {"android", "ios", "react native", "flutter", "swift", "kotlin"},
    ],
    "Cybersecurity Engineer": [
        {"siem", "security monitoring"},
    ],
    "Blockchain Developer": [
        {"ethereum", "web3"},
    ],
}


INFERRED_SKILL_RULES = {
    "api design": {"fastapi", "django", "node.js", "rest api"},
    "backend integration": {"mobile backend integration", "rest api", "api design", "backend", "data retrieval"},
    "databases": {"sql", "postgresql", "mysql", "database design"},
    "testing": {"pytest", "jest", "selenium", "cypress", "test automation", "api testing"},
    "cloud": {"aws", "azure", "gcp"},
    "infrastructure as code": {"terraform"},
    "machine learning": {"scikit-learn", "model evaluation", "feature engineering"},
    "deep learning": {"pytorch", "tensorflow"},
    "model deployment": {"mlops", "docker", "cloud"},
    "data pipelines": {"etl", "airflow", "spark", "kafka"},
    "data warehousing": {"etl", "data modeling", "big data"},
    "application security": {"penetration testing", "vulnerability assessment", "security auditing"},
    "database design": {"data modeling"},
    "query optimization": {"indexing", "stored procedures"},
    "database security": {"identity and access management", "application security", "security auditing"},
    "quality assurance": {"testing", "test automation", "manual testing", "regression testing"},
    "regression testing": {"testing", "test automation", "quality assurance"},
    "risk assessment": {"threat modeling", "vulnerability assessment", "security auditing"},
    "security monitoring": {"siem", "monitoring"},
    "identity and access management": {"authentication", "oauth", "iam"},
    "blockchain": {"ethereum", "web3", "smart contracts", "solidity"},
    "smart contracts": {"solidity"},
    "decentralized applications": {"blockchain", "web3", "ethereum", "smart contracts"},
    "security auditing": {"application security", "vulnerability assessment", "penetration testing"},
    "mobile testing": {"testing", "test automation"},
    "performance optimization": {"web performance", "monitoring", "performance"},
    "software architecture": {"system design"},
}


ROLE_IMPORTANCE = {
    "Software Engineer": {
        "core": {
            "data structures",
            "algorithms",
            "object-oriented programming",
            "system design",
            "api design",
            "git",
            "testing",
        },
        "important": {
            "debugging",
            "design patterns",
            "software architecture",
            "code review",
        },
        "supporting": {"agile"},
    },
    "Frontend Developer": {
        "core": {"html", "css", "javascript", "react", "responsive design", "rest api"},
        "important": {"typescript", "state management", "accessibility", "web performance", "testing"},
        "supporting": {"ui design"},
    },
    "Backend Developer": {
        "core": {"python", "node.js", "fastapi", "django", "sql", "api design", "databases"},
        "important": {"authentication", "microservices", "docker", "testing", "system design"},
        "supporting": set(),
    },
    "Full Stack Developer": {
        "core": {"javascript", "typescript", "react", "node.js", "api design", "sql"},
        "important": {"python", "databases", "authentication", "testing", "docker", "deployment"},
        "supporting": set(),
    },
    "Data Scientist": {
        "core": {"python", "statistics", "machine learning", "pandas", "numpy"},
        "important": {"sql", "data visualization", "data cleaning", "scikit-learn", "feature engineering", "model evaluation"},
        "supporting": {"experimentation"},
    },
    "AI/ML Engineer": {
        "core": {"python", "machine learning", "deep learning", "pytorch", "tensorflow"},
        "important": {"scikit-learn", "feature engineering", "model deployment", "mlops", "docker", "cloud"},
        "supporting": {"llm"},
    },
    "Mobile Developer": {
        "core": {"android", "ios", "react native", "flutter", "swift", "kotlin", "mobile ui"},
        "important": {"mobile testing", "backend integration", "performance optimization", "offline storage"},
        "supporting": {"app store deployment"},
    },
    "Database Engineer": {
        "core": {"sql", "databases", "postgresql", "mysql", "database design", "query optimization"},
        "important": {"indexing", "stored procedures", "etl", "data modeling", "backup and recovery"},
        "supporting": {"database security"},
    },
    "DevOps/Cloud Engineer": {
        "core": {"linux", "docker", "kubernetes", "ci/cd", "terraform", "cloud"},
        "important": {"aws", "azure", "gcp", "monitoring", "infrastructure as code", "scripting"},
        "supporting": set(),
    },
    "QA Engineer": {
        "core": {"testing", "test automation", "manual testing", "selenium", "cypress", "quality assurance"},
        "important": {"pytest", "jest", "test planning", "regression testing", "api testing", "bug tracking"},
        "supporting": set(),
    },
    "Data Engineer": {
        "core": {"python", "sql", "etl", "data pipelines", "airflow", "spark", "databases"},
        "important": {"kafka", "data warehousing", "data modeling", "big data", "cloud"},
        "supporting": set(),
    },
    "Cybersecurity Engineer": {
        "core": {
            "network security",
            "application security",
            "vulnerability assessment",
            "penetration testing",
            "incident response",
            "linux",
        },
        "important": {"siem", "threat modeling", "identity and access management", "security monitoring", "risk assessment"},
        "supporting": {"cryptography"},
    },
    "Blockchain Developer": {
        "core": {"blockchain", "solidity", "smart contracts", "ethereum", "web3", "javascript", "testing"},
        "important": {"cryptography", "decentralized applications", "token standards", "security auditing", "node.js"},
        "supporting": set(),
    },
}


PARTIAL_SKILL_RULES = {
    "debugging": {"testing", "api testing", "quality assurance", "bug tracking", "postman"},
    "design patterns": {"object-oriented programming", "system design", "software architecture"},
    "software architecture": {"system design", "microservices", "software design patterns"},
    "code review": {"git", "github", "gitlab"},
    "agile": {"project management", "scrum", "kanban", "internship", "team"},
    "accessibility": {"ui design", "responsive design"},
    "web performance": {"responsive design", "ssr", "ssg", "csr", "performance"},
    "state management": {"react", "frontend"},
    "authentication": {"backend", "api design", "session management"},
    "microservices": {"backend", "api design", "docker"},
    "deployment": {"docker", "cloud", "aws", "azure", "gcp"},
    "data cleaning": {"pandas", "numpy"},
    "experimentation": {"statistics", "model evaluation"},
    "mlops": {"model deployment", "docker", "cloud"},
    "backend integration": {"mobile backend integration", "rest api", "api design", "backend", "data retrieval"},
    "mobile testing": {"testing", "test automation"},
    "app store deployment": {"mobile app", "deployment"},
    "offline storage": {"session management", "local storage", "mobile app"},
    "database design": {"sql", "databases", "data modeling"},
    "query optimization": {"indexing", "stored procedures", "sql"},
    "stored procedures": {"sql", "databases"},
    "backup and recovery": {"databases", "database security"},
    "database security": {"application security", "identity and access management", "security auditing"},
    "test automation": {"pytest", "jest", "selenium", "cypress", "testing"},
    "test planning": {"quality assurance", "manual testing", "regression testing"},
    "regression testing": {"testing", "quality assurance", "test automation"},
    "bug tracking": {"debugging", "quality assurance"},
    "quality assurance": {"testing", "manual testing", "test automation"},
    "airflow": {"etl", "data pipelines"},
    "spark": {"big data", "data pipelines"},
    "kafka": {"data pipelines", "big data"},
    "data modeling": {"databases", "sql", "data warehousing"},
    "big data": {"spark", "kafka", "data pipelines"},
    "network security": {"linux", "security monitoring"},
    "incident response": {"security monitoring", "siem", "risk assessment"},
    "threat modeling": {"application security", "risk assessment"},
    "identity and access management": {"authentication", "application security"},
    "cryptography": {"blockchain", "application security"},
    "solidity": {"smart contracts", "ethereum", "blockchain"},
    "ethereum": {"blockchain", "web3", "smart contracts"},
    "web3": {"blockchain", "ethereum", "decentralized applications"},
    "decentralized applications": {"blockchain", "web3", "smart contracts"},
    "token standards": {"smart contracts", "ethereum", "solidity"},
    "security auditing": {"application security", "vulnerability assessment", "penetration testing"},
    "mobile ui": {"react native", "flutter", "mobile app", "ui design"},
    "performance optimization": {"performance", "web performance", "monitoring"},
}


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
    detected_names = _detected_skill_names(extracted_skills) | _resume_signal_names(resume_text)
    _add_detected_required_evidence(required_skills, match_evidence, detected_names)
    _add_inferred_match_evidence(required_skills, match_evidence, detected_names)
    _add_frontend_foundation_evidence(required_skills, match_evidence, detected_names, resume_text)
    matched_skills = [skill for skill in required_skills if skill.lower() in match_evidence]

    matched_names = {skill.lower() for skill in matched_skills}
    waived_skills = _alternative_covered_skills(target_role, required_skills, matched_names)
    partial_matches = _partial_match_evidence(
        required_skills,
        matched_names,
        waived_skills,
        detected_names,
        resume_text,
    )
    partial_names = {item["skill"].lower() for item in partial_matches}
    missing_skills = _prioritized_missing_skills(
        target_role,
        [
            skill
            for skill in required_skills
            if skill.lower() not in matched_names and skill.lower() not in waived_skills
        ],
        partial_names,
    )
    coverage = _weighted_coverage(target_role, required_skills, matched_names, waived_skills, partial_names)

    priority_gaps = [
        _gap_priority_item(target_role, skill, partial_names)
        for skill in missing_skills
    ]

    return {
        "target_role": target_role,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "coverage_percent": round(coverage, 1),
        "match_evidence": [match_evidence[skill.lower()] for skill in matched_skills],
        "partial_matches": partial_matches,
        "priority_gaps": priority_gaps,
        "readiness_level": _readiness_level(coverage),
        "waived_skills": [
            {
                "skill": skill,
                "reason": "covered_by_alternative",
            }
            for skill in required_skills
            if skill.lower() in waived_skills
        ],
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


def _priority_for_skill(target_role: str, skill: str) -> str:
    role_importance = ROLE_IMPORTANCE.get(target_role, {})
    skill_key = skill.lower()
    if skill_key in role_importance.get("core", set()):
        return "High"
    if skill_key in role_importance.get("important", set()):
        return "Medium"
    return "Low"


def _skill_weight(target_role: str, skill: str) -> float:
    priority = _priority_for_skill(target_role, skill)
    if priority == "High":
        return 1.4
    if priority == "Medium":
        return 1.0
    return 0.7


def _priority_rank(priority: str) -> int:
    return {"High": 0, "Medium": 1, "Low": 2}.get(priority, 3)


def _prioritized_missing_skills(
    target_role: str,
    missing_skills: list[str],
    partial_names: set[str],
) -> list[str]:
    return sorted(
        missing_skills,
        key=lambda skill: (
            _priority_rank(_priority_for_skill(target_role, skill)),
            1 if skill.lower() in partial_names else 0,
            skill,
        ),
    )


def _gap_priority_item(target_role: str, skill: str, partial_names: set[str]) -> dict:
    return {
        "skill": skill,
        "priority": _priority_for_skill(target_role, skill),
        "status": "partial" if skill.lower() in partial_names else "missing",
    }


def _detected_skill_names(extracted_skills: list[dict]) -> set[str]:
    detected_names = set()
    for item in extracted_skills:
        if _is_confident_extracted_match(item):
            detected_names.add(str(item.get("skill", "")).lower())
    return detected_names


def _resume_signal_names(resume_text: str) -> set[str]:
    searchable_text = resume_text.lower()
    tokens = set(_tokens(searchable_text))
    signals = set()

    if {"java", "c++", "c#", ".net"} & tokens or _contains_phrase(searchable_text, "object oriented"):
        signals.add("object-oriented programming")

    if (
        _contains_phrase(searchable_text, "full-stack system")
        or _contains_phrase(searchable_text, "full stack system")
        or _contains_phrase(searchable_text, "backend apis")
        or _contains_phrase(searchable_text, "scalable frontend systems")
        or _contains_phrase(searchable_text, "system design")
    ):
        signals.add("system design")

    if (
        _contains_phrase(searchable_text, "computer science")
        and ({"java", "c++", "python"} & tokens)
    ):
        signals.add("algorithms")
        signals.add("data structures")

    if _contains_phrase(searchable_text, "postman"):
        signals.add("postman")

    if (
        _contains_phrase(searchable_text, "ssr")
        or _contains_phrase(searchable_text, "ssg")
        or _contains_phrase(searchable_text, "csr")
        or _contains_phrase(searchable_text, "performance")
    ):
        signals.add("performance")

    if (
        _contains_phrase(searchable_text, "intern")
        or _contains_phrase(searchable_text, "team")
        or _contains_phrase(searchable_text, "collaborated")
    ):
        signals.add("team")

    if _contains_phrase(searchable_text, "session management"):
        signals.add("session management")

    if _contains_phrase(searchable_text, "local storage") or _contains_phrase(searchable_text, "offline storage"):
        signals.add("local storage")

    if _contains_phrase(searchable_text, "backend"):
        signals.add("backend")

    if _contains_phrase(searchable_text, "frontend"):
        signals.add("frontend")

    if (
        _contains_phrase(searchable_text, "front-end")
        or _contains_phrase(searchable_text, "front end")
        or _contains_phrase(searchable_text, "web app")
        or _contains_phrase(searchable_text, "web application")
        or _contains_phrase(searchable_text, "website")
    ):
        signals.add("frontend")

    if (
        _contains_phrase(searchable_text, "mobile app")
        or _contains_phrase(searchable_text, "mobile applications")
        or _contains_phrase(searchable_text, "react native")
        or _contains_phrase(searchable_text, "flutter")
    ):
        signals.add("mobile app")

    if (
        ("mobile app" in signals or _contains_phrase(searchable_text, "react native"))
        and (
            _contains_phrase(searchable_text, "backend apis")
            or _contains_phrase(searchable_text, "rest api")
            or _contains_phrase(searchable_text, "data retrieval")
            or _contains_phrase(searchable_text, "automated workflows")
            or _contains_phrase(searchable_text, "ordering")
            or _contains_phrase(searchable_text, "cart")
            or _contains_phrase(searchable_text, "payments")
        )
    ):
        signals.add("mobile backend integration")

    if _contains_phrase(searchable_text, "data retrieval"):
        signals.add("data retrieval")

    return signals


def _partial_match_evidence(
    required_skills: list[str],
    matched_names: set[str],
    waived_skills: set[str],
    detected_names: set[str],
    resume_text: str,
) -> list[dict]:
    available_names = matched_names | detected_names | _resume_signal_names(resume_text)
    partial_matches = []

    for skill in required_skills:
        skill_key = skill.lower()
        if skill_key in matched_names or skill_key in waived_skills:
            continue

        supporting_signals = PARTIAL_SKILL_RULES.get(skill_key, set()) & available_names
        if not supporting_signals:
            continue

        partial_matches.append(
            {
                "skill": skill,
                "source": "transferable",
                "score": PARTIAL_MATCH_CREDIT,
                "matched_alias": ", ".join(sorted(supporting_signals)),
            }
        )

    return partial_matches


def _weighted_coverage(
    target_role: str,
    required_skills: list[str],
    matched_names: set[str],
    waived_skills: set[str],
    partial_names: set[str],
) -> float:
    total_weight = 0.0
    earned_weight = 0.0

    for skill in required_skills:
        skill_key = skill.lower()
        weight = _skill_weight(target_role, skill)
        total_weight += weight

        if skill_key in matched_names or skill_key in waived_skills:
            earned_weight += weight
        elif skill_key in partial_names:
            earned_weight += weight * PARTIAL_MATCH_CREDIT

    return (earned_weight / total_weight * 100) if total_weight else 0.0


def _readiness_level(coverage: float) -> str:
    if coverage >= 80:
        return "strong"
    if coverage >= 60:
        return "competitive"
    if coverage >= 40:
        return "developing"
    return "early"


def _add_detected_required_evidence(
    required_skills: list[str],
    evidence: dict[str, dict],
    detected_names: set[str],
) -> None:
    for skill in required_skills:
        skill_key = skill.lower()
        if skill_key in evidence or skill_key not in detected_names:
            continue

        evidence[skill_key] = {
            "skill": skill,
            "source": "inferred",
            "score": 0.8,
            "matched_alias": "resume context",
        }


def _add_inferred_match_evidence(
    required_skills: list[str],
    evidence: dict[str, dict],
    detected_names: set[str],
) -> None:
    required_lookup = {skill.lower(): skill for skill in required_skills}
    available_names = set(evidence.keys()) | detected_names

    for skill_key, supporting_skills in INFERRED_SKILL_RULES.items():
        if skill_key not in required_lookup or skill_key in evidence:
            continue

        matched_support = sorted(supporting_skills & available_names)
        if not matched_support:
            continue

        evidence[skill_key] = {
            "skill": required_lookup[skill_key],
            "source": "inferred",
            "score": 0.85,
            "matched_alias": ", ".join(matched_support),
        }
        available_names.add(skill_key)


def _add_frontend_foundation_evidence(
    required_skills: list[str],
    evidence: dict[str, dict],
    detected_names: set[str],
    resume_text: str,
) -> None:
    required_lookup = {skill.lower(): skill for skill in required_skills}
    if "html" not in required_lookup or "html" in evidence:
        return

    available_names = set(evidence.keys()) | detected_names
    frontend_context = "frontend" in available_names
    frontend_stack = {"css", "javascript", "typescript", "react"} & available_names
    strong_frontend_stack = {"css", "javascript"} <= available_names or "react" in available_names
    if not frontend_stack or not (frontend_context or strong_frontend_stack):
        return

    evidence["html"] = {
        "skill": required_lookup["html"],
        "source": "inferred",
        "score": 0.85,
        "matched_alias": ", ".join(sorted(frontend_stack)),
    }


def _alternative_covered_skills(
    target_role: str,
    required_skills: list[str],
    matched_names: set[str],
) -> set[str]:
    required_names = {skill.lower() for skill in required_skills}
    covered: set[str] = set()

    for group in ROLE_ALTERNATIVE_GROUPS.get(target_role, []):
        relevant_group = group & required_names
        if relevant_group and relevant_group & matched_names:
            covered.update(relevant_group - matched_names)

    return covered


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
