# Model Handoff

The model owner only needs to edit:

```text
backend/app/services/classification.py
```

Expected function:

```python
def predict_job_role(processed_text: str) -> dict:
    return {
        "role": "Backend Developer",
        "confidence": 0.91,
        "model": "bert_finetuned"
    }
```

Valid role names should match keys in:

```text
backend/app/data/skills_ontology.json
```

If the model returns an unknown role, the report endpoint falls back to the selected role from the frontend.
