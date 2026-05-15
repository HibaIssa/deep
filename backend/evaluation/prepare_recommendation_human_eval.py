import argparse
import csv
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.report_builder import build_resume_report  # noqa: E402


RUBRIC_COLUMNS = [
    "relevance_1_to_5",
    "grounding_1_to_5",
    "specificity_1_to_5",
    "prioritization_1_to_5",
    "format_validity_1_to_5",
    "reviewer_notes",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a CSV sheet for human evaluation of recommendation quality."
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="CSV with resume_path and optional target_role/case_id columns.",
    )
    parser.add_argument("--output", required=True, help="CSV file to write for reviewer scoring.")
    args = parser.parse_args()

    cases = _load_manifest(Path(args.manifest))
    if not cases:
        raise SystemExit("No valid resume cases found in the manifest CSV.")

    review_rows = []
    for index, case in enumerate(cases, start=1):
        case_id = case.get("case_id") or f"case-{index}"
        resume_path = Path(case["resume_path"])
        target_role = case.get("target_role") or None
        report = build_resume_report(resume_path, target_role)
        gap_analysis = report["gap_analysis"]

        for recommendation_index, recommendation in enumerate(report["recommendations"], start=1):
            review_rows.append(
                {
                    "case_id": case_id,
                    "resume_path": str(resume_path),
                    "selected_role": report["selected_role"],
                    "predicted_role": report["predicted_role"].get("role", ""),
                    "prediction_confidence": report["predicted_role"].get("confidence", ""),
                    "coverage_percent": gap_analysis["coverage_percent"],
                    "matched_skills": "; ".join(gap_analysis["matched_skills"]),
                    "missing_skills": "; ".join(gap_analysis["missing_skills"]),
                    "recommendation_number": recommendation_index,
                    "generated_title": recommendation["title"],
                    "generated_detail": recommendation["detail"],
                    "generated_priority": recommendation["priority"],
                    **{column: "" for column in RUBRIC_COLUMNS},
                }
            )

    _write_review_sheet(Path(args.output), review_rows)
    print(f"Wrote {len(review_rows)} recommendation review rows to {args.output}")


def _load_manifest(manifest_path: Path) -> list[dict]:
    with manifest_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if "resume_path" not in (reader.fieldnames or []):
            raise SystemExit("Manifest CSV must include a resume_path column.")

        cases = []
        for row in reader:
            resume_path = (row.get("resume_path") or "").strip()
            if resume_path:
                cases.append(
                    {
                        "case_id": (row.get("case_id") or "").strip(),
                        "resume_path": resume_path,
                        "target_role": (row.get("target_role") or "").strip(),
                    }
                )
        return cases


def _write_review_sheet(output_path: Path, rows: list[dict]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "resume_path",
        "selected_role",
        "predicted_role",
        "prediction_confidence",
        "coverage_percent",
        "matched_skills",
        "missing_skills",
        "recommendation_number",
        "generated_title",
        "generated_detail",
        "generated_priority",
        *RUBRIC_COLUMNS,
    ]
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
