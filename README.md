# Resume Career Advisor

Resume Career Advisor is a full-stack application built around a deep learning resume role classifier. It analyzes a resume, uses a local BERT-based model to predict the most suitable technology role, detects skill gaps against a role ontology, and generates a structured improvement report.

The core intelligence of the system is a local DistilBERT sequence-classification model. Deterministic resume parsing, skill extraction, evidence checking, and optional Gemini-powered review are used around the model to make the prediction explainable, reliable, and useful for career guidance.

## Pipeline

The full report pipeline is orchestrated in `backend/app/services/report_builder.py`.

```text
Resume upload
  -> File validation
  -> Text extraction
  -> Text preprocessing
  -> BERT-based role classification
  -> Prediction evidence check
  -> Target role resolution
  -> Skill extraction
  -> Skill gap detection
  -> Optional Gemini gap refinement
  -> Recommendation generation
  -> Final report response
```

### 1. Resume Upload and Validation

The user uploads a PDF, DOCX, or TXT resume from the React frontend. The backend validates the file type and stores the upload temporarily for analysis.

### 2. Text Extraction

The backend extracts resume text according to file type:

- PDF resumes are parsed page by page.
- DOCX resumes are read from document paragraphs.
- TXT resumes are read directly.

### 3. Text Preprocessing

The extracted text is cleaned and normalized. The preprocessing stage returns:

- processed text
- tokens
- token count
- unique token count
- basic text statistics

### 4. Role Classification

This is the main deep learning stage of the project. A local DistilBERT sequence-classification model reads the processed resume text and predicts the most likely technology role.

DistilBERT is a compact BERT-style transformer model. In this project, it is used for resume text classification: the resume is converted into model tokens, passed through the transformer, and mapped to a job-role label through the classifier head.

The model assets live in:

```text
backend/app/model
```

The inference code lives in:

```text
backend/app/services/classification.py
```

The classifier returns:

- predicted role
- confidence score
- model name

Example output:

```json
{
  "role": "Backend Developer",
  "confidence": 0.91,
  "model": "distilbert_resume_job_classifier"
}
```

### 5. Prediction Evidence Check

The predicted role is not accepted blindly. The pipeline compares the prediction with resume evidence from the skill ontology.

If the prediction has weak support, the report marks the role as:

```text
Cannot decide
```

This happens when confidence, role coverage, or matched role-skill count is too low. The raw model role and confidence are still preserved in the response for transparency.

### 6. Target Role Resolution

The final target role used for gap analysis is chosen in this order:

1. The role selected by the user in the frontend, if valid.
2. The trusted classifier prediction, if valid.
3. The first available role in the ontology as a fallback.

### 7. Skill Extraction

The skill extraction stage identifies technologies and professional skills from the resume using:

- direct keyword matching
- skill aliases
- phrase matching
- conservative weighted matching
- nearby alias matching

### 8. Skill Gap Detection

The detected skills are compared with the selected role's requirements from:

```text
backend/app/data/skills_ontology.json
```

Gap detection is role-aware rather than a flat checklist. It supports:

- direct required-skill matches
- inferred evidence from related tools
- project-context evidence
- alternative technology stacks
- partial transferable matches
- weighted coverage
- readiness levels
- prioritized gaps
- match evidence
- waived skills

The result explains not only which skills are missing, but also why a candidate is considered ready, partially ready, or missing important role requirements.

### 9. Optional Gemini Gap Refinement

When `GEMINI_API_KEY` is configured, the pipeline sends the deterministic gap analysis to Gemini for bounded review.

Gemini may:

- reorder existing priority gaps
- add short reasons
- add concise insight items

Gemini may not:

- invent new skills
- add new matched skills
- add new missing skills
- invent resume experience

If Gemini is unavailable or returns invalid output, the deterministic gap analysis is returned unchanged.

### 10. Recommendation Generation

The recommendation layer generates actionable advice from:

- selected target role
- predicted role
- matched skills
- missing skills
- priority gaps
- match evidence
- resume preview

Gemini is used when configured. Otherwise, the backend falls back to deterministic local recommendations.

### 11. Final Report

The API returns a complete report containing:

- uploaded filename
- predicted role
- selected target role
- extracted skills
- gap analysis
- recommendations
- preprocessing output
- raw text preview

## Tech Stack

- Frontend: React and Vite
- Backend: FastAPI
- Deep learning model: local DistilBERT resume role classifier
- LLM integration: Google Gemini, optional
- Resume parsing: PDF, DOCX, and TXT support
- Evaluation: classifier metrics and human-review recommendation rubric

## Deep Learning Focus

The main model in this project is:

```text
distilbert_resume_job_classifier
```

It is responsible for predicting the resume owner's likely technology role. The surrounding pipeline does not replace the model; it supports the model by preparing clean input, validating the prediction against resume evidence, and using the selected or predicted role to drive skill-gap analysis.

The BERT model is used for:

- understanding resume text context
- classifying resumes into job-role categories
- producing a confidence score for the predicted role
- providing the role signal used by the rest of the career-advice pipeline

The prediction is then checked against extracted skills and ontology coverage. This prevents the system from over-trusting a high-level model prediction when the resume does not contain enough supporting evidence.

## Main API Endpoints

```http
GET /api/report/roles
```

Returns the available target roles from the skill ontology.

```http
POST /api/report/generate
```

Generates the full resume analysis report.

Multipart form fields:

- `file`: required resume file
- `selected_role`: optional target role

## Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173/
```

## Optional Gemini Configuration

Create a project-root `.env` file:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Without Gemini credentials, the application still runs using deterministic local gap detection and recommendation logic.

## Evaluation

Classifier evaluation:

```bash
cd backend
python evaluation/evaluate_classifier.py --input evaluation/classifier_labeled_set.csv --output evaluation/classifier_metrics.json
```

Skill gap regression tests:

```bash
cd backend
python -m unittest discover -s tests
```

Recommendation human-review sheet:

```bash
cd backend
python evaluation/prepare_recommendation_human_eval.py --manifest evaluation/recommendation_eval_manifest.csv --output evaluation/recommendation_human_review.csv
```

Additional architecture, API, model handoff, and evaluation notes are available in the `documentation/` directory.
