# Resume Career Advisor

This project follows the resume analysis pipeline:

1. User uploads a resume.
2. Resume text is extracted and preprocessed.
3. A role classification model predicts a job role.
4. Skills are extracted from the resume.
5. Skill gaps are detected using a role skill ontology, weighted coverage, alternative stacks, inferred evidence, and partial transferable matches.
6. A recommendation layer generates personalized advice from the predicted role and skill gaps.
7. A final report combines role prediction, skill gaps, and advice.

The backend now supports the full resume analysis flow, including local model inference.

## Current status

Implemented pieces:

- Resume upload and file validation
- PDF, DOCX, and TXT text extraction
- Resume cleaning, tokenization, and preprocessing statistics
- Skill extraction using keyword matching, conservative TF-IDF style weighting, and nearby alias matching
- Skill gap detection with role-aware alternatives, inferred matches, partial transferable evidence, readiness levels, and prioritized gaps
- Recommendation generation for missing skills and resume improvements
- React frontend for upload, target role selection, and final report display
- DistilBERT resume job-category classification from `backend/app/model`
- Evaluation scripts for per-class classifier F1 and human review of recommendation quality

The LLM recommendation layer uses Google Gemini when `GEMINI_API_KEY` is present, with a deterministic local fallback in `backend/app/services/llm_recommendation.py`. The LLM prompt and evaluation approach are documented in `documentation/model_handoff.md`.

Evaluation details and commands are documented in `documentation/evaluation.md`.

## Run

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173/`.
