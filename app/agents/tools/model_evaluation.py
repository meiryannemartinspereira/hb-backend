import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
)


ROOT = Path(__file__).resolve().parents[1]


def evaluate_predictions(input_path):
    df = pd.read_csv(input_path)

    required = {"y_true", "y_pred"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {sorted(missing)}"
        )

    if df[list(required)].isna().any().any():
        raise ValueError("Existem valores ausentes nas previsões.")

    y_true = df["y_true"]
    y_pred = df["y_pred"]

    labels = sorted(
        set(y_true.unique()) | set(y_pred.unique()),
        key=str
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    return {
        "tool": "model_evaluation",
        "file": str(input_path),
        "rows_evaluated": int(len(df)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(
            balanced_accuracy_score(y_true, y_pred)
        ),
        "labels": [str(label) for label in labels],
        "confusion_matrix": matrix.tolist(),
        "classification_report": report,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        required=True,
        help="CSV com as colunas y_true e y_pred"
    )
    parser.add_argument(
        "--output",
        default="reports/model_evaluation.json"
    )
    args = parser.parse_args()

    input_path = ROOT / args.input
    output_path = ROOT / args.output

    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    result = evaluate_predictions(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nRelatório salvo em: {output_path}")


if __name__ == "__main__":
    main()