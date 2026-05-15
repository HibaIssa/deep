import json
import math
import re
from collections import Counter

from app.config import DATA_DIR


SKILL_ALIASES = {
    "accessibility": {"accessibility", "a11y", "wcag"},
    "agile": {"agile", "scrum", "kanban"},
    "algorithms": {"algorithms", "algorithmic"},
    "api design": {"api design", "rest api", "restful api", "api architecture", "apis"},
    "api testing": {"api testing", "postman", "rest api testing"},
    "application security": {"application security", "appsec"},
    "authentication": {"authentication", "auth", "oauth", "jwt"},
    "azure": {"azure", "microsoft azure"},
    "big data": {"big data", "distributed data"},
    "blockchain": {"blockchain"},
    "backend integration": {"backend integration", "integrated backend", "connected to backend"},
    "cloud": {"cloud", "cloud computing"},
    "code review": {"code review", "code reviews", "pull request review", "pr review"},
    "data cleaning": {"data cleaning", "data preprocessing", "data wrangling"},
    "data modeling": {"data modeling", "data modelling"},
    "data structures": {"data structures", "data structure"},
    "data visualization": {"data visualization", "dashboarding", "tableau", "power bi", "dashboards"},
    "database design": {"database design", "schema design"},
    "database security": {"database security", "db security"},
    "databases": {"database", "databases", "dbms"},
    "debugging": {"debugging", "debug"},
    "deep learning": {"deep learning", "dl", "neural networks"},
    "deployment": {"deployment", "deployments", "deploy"},
    "design patterns": {"design patterns", "software design patterns"},
    "django": {"django"},
    "docker": {"docker", "containerization", "containers"},
    "etl": {"etl", "elt"},
    "experimentation": {"experimentation", "a/b testing", "ab testing", "experiments"},
    "fastapi": {"fastapi", "fast api"},
    "feature engineering": {"feature engineering"},
    "flutter": {"flutter"},
    "html": {"html", "html5"},
    "incident response": {"incident response", "ir"},
    "indexing": {"indexing", "database indexing"},
    "ios": {"ios"},
    "jest": {"jest"},
    "javascript": {"js", "javascript"},
    "kafka": {"kafka", "apache kafka"},
    "kotlin": {"kotlin"},
    "linux": {"linux"},
    "llm": {"llm", "llms", "large language model", "large language models", "generative ai"},
    "machine learning": {"machine learning", "ml"},
    "manual testing": {"manual testing"},
    "microservices": {"microservices", "microservice"},
    "mlops": {"mlops", "machine learning operations"},
    "model deployment": {"model deployment", "deploying models"},
    "model evaluation": {"model evaluation", "model validation"},
    "monitoring": {"monitoring", "observability"},
    "mysql": {"mysql"},
    "network security": {"network security", "network hardening"},
    "node.js": {"node", "node.js", "nodejs"},
    "numpy": {"numpy", "num py"},
    "object-oriented programming": {"object-oriented programming", "object oriented programming", "oop"},
    "pandas": {"pandas"},
    "performance optimization": {"performance optimization", "performance tuning"},
    "postgresql": {"postgres", "postgresql"},
    "pytorch": {"pytorch", "py torch"},
    "python": {"python", "py"},
    "pytest": {"pytest"},
    "query optimization": {"query optimization", "query tuning"},
    "react": {"react", "react.js", "reactjs"},
    "regression testing": {"regression testing"},
    "responsive design": {"responsive design"},
    "rest api": {"rest api", "restful api", "apis"},
    "risk assessment": {"risk assessment"},
    "scikit-learn": {"scikit-learn", "scikit learn", "sklearn", "sci-kit learn"},
    "selenium": {"selenium"},
    "security monitoring": {"security monitoring"},
    "software architecture": {"software architecture", "software architectures"},
    "spark": {"spark", "apache spark"},
    "sql": {"sql", "postgres", "postgresql", "mysql", "sqlite"},
    "state management": {"state management", "redux", "zustand"},
    "statistics": {"statistics", "statistical analysis", "stats"},
    "swift": {"swift"},
    "system design": {"system design", "systems design"},
    "tensorflow": {"tensorflow", "tensor flow"},
    "test automation": {"test automation", "automated testing"},
    "test planning": {"test planning", "test plans"},
    "testing": {"testing", "unit testing", "pytest", "jest", "tests"},
    "threat modeling": {"threat modeling", "threat modelling"},
    "ui design": {"ui design", "user interface design"},
    "vulnerability assessment": {"vulnerability assessment", "vulnerability scanning"},
    "web performance": {"web performance", "frontend performance"},
    "web3": {"web3", "web 3"},
    "typescript": {"ts", "typescript"},
    "ci/cd": {"ci/cd", "cicd", "ci cd", "continuous integration", "continuous deployment"},
    "kubernetes": {"kubernetes", "k8s"},
    "infrastructure as code": {"infrastructure as code", "iac"},
    "aws": {"aws", "amazon web services"},
    "gcp": {"gcp", "google cloud", "google cloud platform"},
    "identity and access management": {"identity and access management", "iam"},
    "siem": {"siem", "security information and event management"},
    "penetration testing": {"penetration testing", "pentesting", "pen testing"},
    "data pipelines": {"data pipeline", "data pipelines"},
    "data warehousing": {"data warehouse", "data warehousing"},
    "react native": {"react native", "react-native"},
    "app store deployment": {"app store deployment", "play store deployment"},
    "git": {"git", "github", "gitlab"},
}


MIN_SINGLE_TOKEN_TFIDF_SCORE = 0.24


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
        if len(_tokens(skill)) != 1:
            continue

        threshold = MIN_SINGLE_TOKEN_TFIDF_SCORE
        if score >= threshold:
            results[skill] = {
                "skill": skill,
                "source": "tf-idf",
                "score": round(score, 3),
            }

    for skill in ontology_skills:
        if skill in results:
            continue
        semantic_score = _semantic_overlap(skill, tokens)
        if semantic_score >= 1.0:
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
    return re.search(rf"(?<![a-z0-9+#-]){escaped}(?![a-z0-9+#-])", text) is not None


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
    candidate_phrases = {skill, *SKILL_ALIASES.get(skill, set())}
    return max((_nearby_term_overlap(phrase, tokens) for phrase in candidate_phrases), default=0.0)


def _nearby_term_overlap(phrase: str, tokens: list[str]) -> float:
    phrase_terms = _tokens(phrase)
    if not phrase_terms:
        return 0.0
    if len(phrase_terms) == 1:
        return 1.0 if phrase_terms[0] in tokens else 0.0

    window_size = min(max(len(phrase_terms) + 3, 4), 7)
    best_overlap = 0.0
    for index in range(len(tokens)):
        window_terms = set(tokens[index : index + window_size])
        overlap = len(set(phrase_terms) & window_terms) / len(set(phrase_terms))
        best_overlap = max(best_overlap, overlap)
        if best_overlap >= 1.0:
            break

    return best_overlap
