import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def validate_temporal(input_path, time_column):
    df = pd.read_csv(input_path)

    if time_column not in df.columns:
        raise ValueError(
            f"Coluna temporal '{time_column}' não encontrada. "
            f"Colunas disponíveis: {list(df.columns)}"
        )

    values = df[time_column]

    if time_column == "timestamp":
        parsed = pd.to_datetime(values, errors="coerce", utc=True)
    else:
        parsed = pd.to_numeric(values, errors="coerce")

    valid = parsed.dropna()
    differences = valid.diff().dropna()

    result = {
        "tool": "temporal_validation",
        "file": str(input_path),
        "time_column": time_column,
        "total_rows": int(len(df)),
        "invalid_timestamps": int(parsed.isna().sum()),
        "duplicate_timestamps": int(parsed.duplicated().sum()),
        "strictly_increasing": bool(
            len(valid) > 1 and valid.is_monotonic_increasing
            and not valid.duplicated().any()
        ),
        "non_increasing_steps": int((differences <= 0).sum()),
        "missing_intervals_detected": None,
        "first_timestamp": (
            str(valid.iloc[0]) if len(valid) else None
        ),
        "last_timestamp": (
            str(valid.iloc[-1]) if len(valid) else None
        ),
    }

    if time_column == "timestamp" and len(differences):
        result["median_interval_seconds"] = float(
            differences.dt.total_seconds().median()
        )
        result["missing_intervals_detected"] = int(
            (
                differences.dt.total_seconds()
                > differences.dt.total_seconds().median() * 1.5
            ).sum()
        )
    elif time_column != "timestamp" and len(differences):
        result["median_interval"] = float(differences.median())
        result["missing_intervals_detected"] = int(
            (differences > differences.median() * 1.5).sum()
        )

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/dataset_ml_1day.csv"
    )
    parser.add_argument("--time-column", default="timestamp")
    parser.add_argument(
        "--output",
        default="reports/temporal_validation.json"
    )
    args = parser.parse_args()

    input_path = ROOT / args.input
    output_path = ROOT / args.output

    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    result = validate_temporal(input_path, args.time_column)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nRelatório salvo em: {output_path}")


if __name__ == "__main__":
    main()