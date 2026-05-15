from functools import lru_cache
from pathlib import Path
import warnings


MODEL_DIR = Path(__file__).resolve().parents[1] / "model"
MODEL_NAME = "distilbert_resume_job_classifier"
MAX_LENGTH = 512


@lru_cache(maxsize=1)
def _load_model_assets():
    import joblib
    import torch
    from sklearn.exceptions import InconsistentVersionWarning
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_DIR,
        local_files_only=True,
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
        label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, label_encoder, device, torch


def predict_job_role(processed_text: str) -> dict:
    """Predict the most likely job category for cleaned resume text."""
    if not processed_text or not processed_text.strip():
        return {
            "role": "Unknown",
            "confidence": 0.0,
            "model": MODEL_NAME,
        }

    tokenizer, model, label_encoder, device, torch = _load_model_assets()
    encoded = tokenizer(
        processed_text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=MAX_LENGTH,
    )
    encoded.pop("token_type_ids", None)
    encoded = {key: value.to(device) for key, value in encoded.items()}

    with torch.no_grad():
        logits = model(**encoded).logits
        probabilities = torch.softmax(logits, dim=-1)[0]
        confidence, predicted_index = torch.max(probabilities, dim=0)

    label_id = int(predicted_index.item())
    role = str(label_encoder.inverse_transform([label_id])[0])

    return {
        "role": role,
        "confidence": round(float(confidence.item()), 4),
        "model": MODEL_NAME,
    }
