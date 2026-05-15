import re
from dataclasses import dataclass


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


@dataclass(frozen=True)
class PreprocessingResult:
    processed_text: str
    tokens: list[str]
    stats: dict[str, int]


def preprocess_resume_text(raw_text: str) -> PreprocessingResult:
    cleaned_text = clean_resume_text(raw_text)
    tokens = tokenize_resume_text(cleaned_text)
    filtered_tokens = [token for token in tokens if token not in STOP_WORDS and len(token) > 1]

    return PreprocessingResult(
        processed_text=" ".join(filtered_tokens),
        tokens=filtered_tokens,
        stats={
            "raw_characters": len(raw_text),
            "cleaned_characters": len(cleaned_text),
            "token_count": len(filtered_tokens),
            "unique_token_count": len(set(filtered_tokens)),
        },
    )


def clean_resume_text(raw_text: str) -> str:
    text = raw_text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", " ", text)
    text = re.sub(r"\+?\d[\d\s().-]{7,}\d", " ", text)
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_resume_text(cleaned_text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#.]+(?:-[a-z0-9+#.]+)?", cleaned_text)
