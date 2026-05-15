# API Reference

## `GET /`

Health check.

## `POST /api/resume/upload`

Uploads a resume and returns preprocessing output.

Multipart fields:

- `file`: `.pdf`, `.docx`, or `.txt`

## `GET /api/report/roles`

Returns role names from the skill ontology.

## `POST /api/report/generate`

Uploads a resume and returns the full report.

Multipart fields:

- `file`: `.pdf`, `.docx`, or `.txt`
- `selected_role`: optional target role

Response sections:

- `predicted_role`
- `selected_role`
- `extracted_skills`
- `gap_analysis`
- `recommendations`
- `preprocessing`
- `raw_text_preview`

### `gap_analysis`

`gap_analysis` contains both the simple fields used by the UI and additional explanation fields:

- `target_role`: role used for the comparison
- `required_skills`: ontology skills for the role
- `matched_skills`: skills considered covered by direct, phrase, alias, or inferred evidence
- `missing_skills`: remaining gaps, ordered by priority instead of raw ontology order
- `coverage_percent`: weighted readiness score
- `readiness_level`: one of `early`, `developing`, `competitive`, or `strong`
- `match_evidence`: evidence for each matched skill, including source and matched alias/context
- `partial_matches`: transferable evidence that partially supports a missing skill
- `priority_gaps`: missing or partial gaps with `High`, `Medium`, or `Low` priority
- `waived_skills`: skills not counted as gaps because an equivalent alternative is covered
- `llm_refinement`: optional Gemini gap-review metadata with model name and validated insight items

Example:

```json
{
  "target_role": "Software Engineer",
  "required_skills": ["data structures", "algorithms", "api design", "git", "testing"],
  "matched_skills": ["data structures", "algorithms", "api design", "git", "testing"],
  "missing_skills": ["code review", "debugging", "agile"],
  "coverage_percent": 79.7,
  "readiness_level": "competitive",
  "match_evidence": [
    {
      "skill": "api design",
      "source": "keyword",
      "score": 1.0,
      "matched_alias": null
    }
  ],
  "partial_matches": [
    {
      "skill": "debugging",
      "source": "transferable",
      "score": 0.25,
      "matched_alias": "api testing, postman, testing"
    }
  ],
  "priority_gaps": [
    {
      "skill": "debugging",
      "priority": "Medium",
      "status": "partial",
      "reason": "Testing and Postman evidence partially support debugging, but the resume should show direct defect-resolution examples."
    }
  ],
  "waived_skills": [],
  "llm_refinement": {
    "enabled": true,
    "model": "gemini-2.5-flash",
    "insights": [
      {
        "title": "Show direct debugging evidence",
        "detail": "The resume has related testing evidence, but stronger debugging bullets would improve role alignment.",
        "priority": "Medium"
      }
    ]
  }
}
```
