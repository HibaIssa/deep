# Evaluation

The project evaluates two separate quality surfaces:

- Role classification quality with per-class precision, recall, and F1-score.
- Skill gap quality with regression cases for direct, inferred, alternative, partial, and prioritized gap behavior.
- Recommendation quality with a small human review rubric.

## Classifier Metrics

Create a labeled CSV with at least these columns:

```csv
text,label
"Python FastAPI SQL resume text...",Backend Developer
"SOC monitoring SIEM incident response resume text...",Cybersecurity Analyst
```

Run the evaluator from the `backend` directory:

```bash
python evaluation/evaluate_classifier.py --input evaluation/classifier_labeled_set.csv --output evaluation/classifier_metrics.json
```

The script prints accuracy plus a full per-class report:

- precision
- recall
- F1-score
- support

It also writes a JSON artifact when `--output` is provided. Use macro F1 to judge whether the classifier works evenly across roles, and weighted F1 to summarize performance when the labeled set is imbalanced.

If the CSV text is already preprocessed, add:

```bash
python evaluation/evaluate_classifier.py --input evaluation/classifier_labeled_set.csv --already-processed
```

## Skill Gap Regression Tests

Skill gap detection is evaluated with unit tests in:

```text
backend/tests/test_skill_gap_detection.py
```

Run from the `backend` directory:

```bash
python -m unittest discover -s tests
```

The tests cover:

- direct skill and alias matches
- false-positive prevention for broad multi-word skills
- inferred matches, such as `api design` from backend framework evidence
- role-specific alternatives, such as FastAPI/Django/Node.js or AWS/Azure/GCP/cloud
- resume-context signals, such as Computer Science coursework plus Java/C++/Python supporting algorithms and data structures
- partial transferable matches, such as Git partially supporting code review or Postman/API testing partially supporting debugging
- priority ordering for gaps

Manual review should check that the detector stays realistic: it should not overclaim skills, but it should avoid harsh checklist behavior when a resume shows equivalent stack experience or transferable evidence.

## Recommendation Human Review

Create a small manifest of representative resumes:

```csv
case_id,resume_path,target_role
backend-1,app/uploads/backend_resume.pdf,Backend Developer
data-1,app/uploads/data_resume.pdf,Data Scientist
```

Generate a review sheet:

```bash
python evaluation/prepare_recommendation_human_eval.py --manifest evaluation/recommendation_eval_manifest.csv --output evaluation/recommendation_human_review.csv
```

Reviewers score each generated recommendation from 1 to 5 on:

- relevance: addresses the target role and detected gaps
- grounding: avoids unsupported claims about the resume
- specificity: gives concrete next steps
- prioritization: ranks important gaps first and handles partial gaps appropriately
- format validity: keeps the expected title/detail/priority structure

Average the scores by recommendation and by case. A useful minimum gate is an average score of 4 or higher for relevance and grounding, because those two categories most directly protect user trust.
