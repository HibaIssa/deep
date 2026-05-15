def predict_job_role(processed_text: str) -> dict:
    """Model integration boundary.

    Keep this lightweight until the BERT/LSTM model package is merged by the model owner.
    The rest of the app can call this function without knowing which model is used.
    """
    return {
        "role": "Pending model integration",
        "confidence": 0.0,
        "model": "external_model_placeholder",
    }
