# Architecture

## Flow

```text
User uploads resume
  -> Resume parser extracts text from PDF/DOCX/TXT
  -> Preprocessing cleans and tokenizes text
  -> Classification boundary calls external model placeholder
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
- `services/classification.py`: model integration boundary
- `services/skill_extraction.py`: keyword, TF-IDF style, and semantic alias matching
- `services/gap_detection.py`: ontology comparison
- `services/llm_recommendation.py`: recommendation generation
- `services/report_builder.py`: orchestrates the full non-model pipeline

## Model boundary

The rest of the app expects `predict_job_role(processed_text)` to return a dictionary with `role`, `confidence`, and `model`.
