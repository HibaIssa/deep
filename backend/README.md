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

## Model handoff

The classifier integration point is `app/services/classification.py`.

Your teammate can replace `predict_job_role(processed_text)` with a BERT or LSTM inference call as long as it returns:

```json
{
  "role": "Backend Developer",
  "confidence": 0.91,
  "model": "bert_finetuned"
}
```
