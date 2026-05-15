# Resume Career Advisor Backend

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The first implemented API slice is:

```http
POST /api/resume/upload
```

Upload a `.pdf`, `.docx`, or `.txt` resume as multipart form data using the `file` field.

## Main endpoints

```http
GET /api/report/roles
```

Returns the available job roles from `app/data/skills_ontology.json`.

```http
POST /api/report/generate
```

Multipart form fields:

- `file`: resume file, required
- `selected_role`: role name, optional

This runs every non-model step: parsing, preprocessing, skill extraction, skill gap detection, and recommendation generation.

## Model inference

The classifier integration point is `app/services/classification.py`. It loads the local DistilBERT sequence-classification model from:

```text
app/model
```

`predict_job_role(processed_text)` returns:

```json
{
  "role": "Backend Developer",
  "confidence": 0.91,
  "model": "distilbert_resume_job_classifier"
}
```

## Gemini recommendations

The recommendation service uses Google Gemini when `GEMINI_API_KEY` is set in the project-root `.env` file:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

If the key is missing or the API call fails, the backend falls back to deterministic local recommendations.

## Evaluation

Classifier metrics:

```bash
python evaluation/evaluate_classifier.py --input evaluation/classifier_labeled_set.csv --output evaluation/classifier_metrics.json
```

This reports accuracy plus per-class precision, recall, and F1-score.

Recommendation human-review sheet:

```bash
python evaluation/prepare_recommendation_human_eval.py --manifest evaluation/recommendation_eval_manifest.csv --output evaluation/recommendation_human_review.csv
```

The generated CSV includes 1-5 rubric columns for relevance, grounding, specificity, prioritization, and format validity.
