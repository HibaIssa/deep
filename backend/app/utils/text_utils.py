def preview_text(text: str, limit: int = 500) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."
