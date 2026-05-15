# Architecture

## Flow

```text
User uploads resume
  -> Resume parser extracts text from PDF/DOCX/TXT
  -> Preprocessing cleans and tokenizes text
  -> Classification service runs the local DistilBERT model
  -> Skill extraction finds resume skills
  -> Gap detection compares skills with ontology
  -> Recommendation module creates improvement advice
  -> Final report is returned to the frontend
```

## Backend modules

- `routes/resume_routes.py`: basic upload and preprocessing endpoint
- `routes/report_routes.py`: full report endpoint and role list endpoint
- `services/resume_parser.py`: file text extraction
- `services/preprocessing.py`: cleaning, tokenization, and stats
- `services/classification.py`: local DistilBERT classifier inference
- `services/skill_extraction.py`: keyword, TF-IDF style, and semantic alias matching
- `services/gap_detection.py`: ontology comparison
- `services/llm_recommendation.py`: recommendation generation; currently deterministic fallback logic, with the planned LLM prompt contract documented in `model_handoff.md`
- `services/report_builder.py`: orchestrates the full non-model pipeline
- `evaluation/evaluate_classifier.py`: classifier evaluation with per-class precision, recall, and F1-score
- `evaluation/prepare_recommendation_human_eval.py`: generates a CSV for human review of recommendation quality

## Model boundary

The rest of the app expects `predict_job_role(processed_text)` to return a dictionary with `role`, `confidence`, and `model`.

## Recommendation boundary

The LLM integration uses Google Gemini through the Gemini REST `generateContent` API. It receives structured output from classification and gap detection: predicted role, selected target role, matched skills, missing skills, required skills, and coverage percentage. It should return validated JSON recommendation items with `title`, `detail`, and `priority`.

The app keeps the deterministic recommendation generator as an offline fallback so the report endpoint still works without LLM credentials or network access.
