import argparse
import csv
import json
import sys
from pathlib import Path

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.classification import predict_job_role  # noqa: E402
from app.services.preprocessing import preprocess_resume_text  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the resume role classifier with per-class precision, recall, and F1-score."
    )
    parser.add_argument("--input", required=True, help="CSV file with resume text and gold labels.")
    parser.add_argument("--text-column", default="text", help="Column containing resume text.")
    parser.add_argument("--label-column", default="label", help="Column containing the expected role label.")
    parser.add_argument(
        "--already-processed",
        action="store_true",
        help="Use text-column as already-cleaned model input instead of running preprocessing.",
    )
    parser.add_argument("--output", help="Optional JSON output path for metrics and predictions.")
    args = parser.parse_args()

    rows = _load_rows(Path(args.input), args.text_column, args.label_column)
    if not rows:
        raise SystemExit("No valid labeled rows found in the input CSV.")

    y_true: list[str] = []
    y_pred: list[str] = []
    predictions: list[dict] = []

    for index, row in enumerate(rows, start=1):
        model_input = row["text"]
        if not args.already_processed:
            model_input = preprocess_resume_text(model_input).processed_text

        prediction = predict_job_role(model_input)
        expected_label = row["label"]
        predicted_label = prediction["role"]

        y_true.append(expected_label)
        y_pred.append(predicted_label)
        predictions.append(
            {
                "row": index,
                "expected_label": expected_label,
                "predicted_label": predicted_label,
                "confidence": prediction.get("confidence", 0.0),
                "correct": expected_label == predicted_label,
            }
        )

    labels = sorted(set(y_true) | set(y_pred))
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )
    matrix = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    result = {
        "total_examples": len(y_true),
        "accuracy": accuracy_score(y_true, y_pred),
        "labels": labels,
        "classification_report": report,
        "confusion_matrix": matrix,
        "predictions": predictions,
    }

    print(f"Total examples: {result['total_examples']}")
    print(f"Accuracy: {result['accuracy']:.4f}")
    print()
    print(
        classification_report(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0,
        )
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Wrote metrics JSON to {output_path}")


def _load_rows(input_path: Path, text_column: str, label_column: str) -> list[dict]:
    with input_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing_columns = {text_column, label_column} - set(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise SystemExit(f"Input CSV is missing required column(s): {missing}")

        rows = []
        for row in reader:
            text = (row.get(text_column) or "").strip()
            label = (row.get(label_column) or "").strip()
            if text and label:
                rows.append({"text": text, "label": label})
        return rows


if __name__ == "__main__":
    main()
