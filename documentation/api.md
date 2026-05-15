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
