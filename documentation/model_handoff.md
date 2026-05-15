# Model Integration

The trained resume classifier is integrated in:

```text
backend/app/services/classification.py
```

It loads these local model assets from `backend/app/model`:

- `config.json`
- `model.safetensors`
- `tokenizer.json`
- `tokenizer_config.json`
- `label_encoder.pkl`

The public function remains:

```python
def predict_job_role(processed_text: str) -> dict:
    return {
        "role": "Backend Developer",
        "confidence": 0.91,
        "model": "distilbert_resume_job_classifier"
    }
```

The model can predict all labels stored in `label_encoder.pkl`. If a predicted role is not present in `backend/app/data/skills_ontology.json`, the report endpoint still uses the selected frontend role for skill-gap analysis.

## LLM recommendation plan

The recommendation layer is designed for an API-based instruction-following LLM rather than a locally hosted model. The current production setup is:

- Primary option: Google Gemini through the Gemini REST `generateContent` API, configured with `GEMINI_API_KEY`.
- Default model: `gemini-2.5-flash`, overridable with `GEMINI_MODEL`.
- Gap refinement: `backend/app/services/llm_gap_refinement.py` can call Gemini after deterministic gap detection to refine priority ordering, add reasons, and produce concise insights without changing the trusted deterministic matched/missing skill sets.
- Local/offline fallback: the deterministic implementations in `backend/app/services/gap_detection.py` and `backend/app/services/llm_recommendation.py`, which keep the pipeline usable without network credentials.

This keeps the app easy to demo without network credentials while leaving a clear boundary for adding real LLM calls later.

### Prompt construction

The LLM prompt should be built from structured pipeline output, not raw resume text alone. The prompt will include:

- The classifier output: predicted role, confidence, and model name.
- The selected target role used for analysis.
- Matched skills from the resume.
- Missing skills from the ontology comparison.
- Coverage percentage, readiness level, and the full required-skill list for the role.
- Priority gaps, including whether each gap is fully missing or partially supported by transferable evidence.
- Match evidence and partial-match evidence when useful for grounding recommendations.
- Skills waived because an equivalent alternative stack is covered.
- Optional validated LLM gap-refinement insights.
- A short resume preview only if needed for personalization.

The system instruction should constrain the model to act as a career-advice assistant and return concise, evidence-based suggestions. The user payload should be JSON-like structured data, for example:

```text
System:
You are a career advisor. Generate practical resume and learning recommendations.
Use only the provided classification and skill-gap data. Do not invent skills or experience.
Return JSON with 3-5 items. Each item must include title, detail, and priority.

User:
{
  "predicted_role": {"role": "Backend Developer", "confidence": 0.91},
  "target_role": "Backend Developer",
  "coverage_percent": 70.0,
  "readiness_level": "competitive",
  "matched_skills": ["python", "fastapi", "sql", "api design", "databases", "testing"],
  "missing_skills": ["authentication", "microservices", "system design"],
  "required_skills": ["python", "node.js", "fastapi", "django", "sql", "api design", "databases", "authentication", "microservices", "docker", "testing", "system design"],
  "priority_gaps": [
    {"skill": "authentication", "priority": "Medium", "status": "partial"},
    {"skill": "microservices", "priority": "Medium", "status": "partial"},
    {"skill": "system design", "priority": "Medium", "status": "missing"}
  ],
  "partial_matches": [
    {"skill": "authentication", "source": "transferable", "matched_alias": "backend, api design"}
  ],
  "waived_skills": [
    {"skill": "node.js", "reason": "covered_by_alternative"},
    {"skill": "django", "reason": "covered_by_alternative"}
  ]
}
```

The backend should validate the returned JSON before sending it to the frontend. If validation fails, it should fall back to the deterministic recommendation function.

### Quality evaluation

Classifier quality should be evaluated with a labeled CSV and `backend/evaluation/evaluate_classifier.py`. The report includes accuracy, but the primary checks are per-class precision, recall, and F1-score so weak role categories are visible instead of hidden by a single aggregate number.

Recommendation quality is evaluated with a small labeled test set of resumes and target roles. Use `backend/evaluation/prepare_recommendation_human_eval.py` to generate a reviewer CSV. Each generated recommendation should be scored on:

- Relevance: addresses the selected role and the detected gaps.
- Grounding: does not invent resume experience or unsupported skills.
- Specificity: gives concrete next steps, projects, courses, or resume edits.
- Prioritization: ranks high-impact gaps first and treats partial gaps differently from fully missing skills.
- Format validity: returns the expected JSON structure for the frontend.

For development, these checks can be run manually with representative resumes. The concrete commands and CSV formats are documented in `documentation/evaluation.md`. For a later production version, the same criteria can become an automated rubric plus regression tests that compare LLM output against expected role/gap coverage.
