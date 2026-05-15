# Architecture

## Flow

```text
User uploads resume
  -> Resume parser extracts text from PDF/DOCX/TXT
  -> Preprocessing cleans and tokenizes text
  -> Classification service runs the local DistilBERT model
  -> Skill extraction finds resume skills
  -> Gap detection compares skills with ontology using weighted, role-aware matching
  -> Recommendation module creates improvement advice
  -> Final report is returned to the frontend
```

## Backend modules

- `routes/resume_routes.py`: basic upload and preprocessing endpoint
- `routes/report_routes.py`: full report endpoint and role list endpoint
- `services/resume_parser.py`: file text extraction
- `services/preprocessing.py`: cleaning, tokenization, and stats
- `services/classification.py`: local DistilBERT classifier inference
- `services/skill_extraction.py`: keyword, conservative TF-IDF style, and nearby alias matching
- `services/gap_detection.py`: role-aware ontology comparison with direct matches, inferred matches, alternative stacks, partial transferable evidence, weighted coverage, readiness labels, and prioritized gaps
- `services/llm_recommendation.py`: recommendation generation; currently deterministic fallback logic, with the planned LLM prompt contract documented in `model_handoff.md`
- `services/report_builder.py`: orchestrates the full non-model pipeline
- `evaluation/evaluate_classifier.py`: classifier evaluation with per-class precision, recall, and F1-score
- `evaluation/prepare_recommendation_human_eval.py`: generates a CSV for human review of recommendation quality

## Model boundary

The rest of the app expects `predict_job_role(processed_text)` to return a dictionary with `role`, `confidence`, and `model`.

## Gap detection behavior

Gap detection is not a flat keyword checklist. The service starts with the selected target role's required skills, then builds evidence from:

- directly extracted skills from the resume
- exact phrase and alias matches
- inferred skills, such as `api design` from FastAPI/Django/Node.js or `testing` from pytest/Jest/Postman/API testing
- project-context skills, such as `backend integration` for mobile apps only when the resume shows mobile work connected to backend APIs, data retrieval, workflows, ordering, carts, or payments
- role-specific alternative groups, such as FastAPI/Django/Node.js for backend frameworks or AWS/Azure/GCP/cloud for cloud coverage
- partial transferable evidence, such as Git partially supporting code-review readiness or API testing/Postman partially supporting debugging

Coverage is weighted by role importance. Core skills count more than supporting skills, alternative groups avoid over-penalizing equivalent stacks, and partial matches receive limited credit. The response also includes `readiness_level`, `priority_gaps`, `partial_matches`, `match_evidence`, and `waived_skills` so the frontend and recommendation layer can explain the result.

## Recommendation boundary

The LLM integration uses Google Gemini through the Gemini REST `generateContent` API. It receives structured output from classification and gap detection: predicted role, selected target role, matched skills, missing skills, required skills, coverage percentage, readiness level, prioritized gaps, partial matches, and match evidence. It should return validated JSON recommendation items with `title`, `detail`, and `priority`.

The app keeps the deterministic recommendation generator as an offline fallback so the report endpoint still works without LLM credentials or network access.
