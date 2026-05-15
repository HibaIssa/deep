# Resume Career Advisor

This project follows the resume analysis pipeline:

1. User uploads a resume.
2. Resume text is extracted and preprocessed.
3. A role classification model predicts a job role.
4. Skills are extracted from the resume.
5. Missing skills are detected using a role skill ontology.
6. An LLM generates personalized recommendations.
7. A final report combines role prediction, skill gaps, and advice.

The first implemented milestone is resume upload and preprocessing.

## Current status

Everything outside the classifier model is implemented:

- Resume upload and file validation
- PDF, DOCX, and TXT text extraction
- Resume cleaning, tokenization, and preprocessing statistics
- Skill extraction using keyword matching, TF-IDF style weighting, and alias-based semantic matching
- Skill gap detection against a role skill ontology
- Recommendation generation for missing skills and resume improvements
- React frontend for upload, target role selection, and final report display

The model is intentionally left as a placeholder in `backend/app/services/classification.py` because the model work is owned separately.

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
