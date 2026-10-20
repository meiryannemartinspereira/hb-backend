import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def validate_data(input_path, target):
    df = pd.read_csv(input_path)

    numeric = df.select_dtypes(include="number")
    missing = df.isna().sum()
    infinite = pd.Series(
        np.isinf(numeric).sum(),
        index=numeric.columns
    )
    constant = [
        column
        for column in df.columns
        if df[column].nunique(dropna=False) <= 1
    ]

    result = {
        "tool": "data_quality",
        "file": str(input_path),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_values": {
            key: int(value)
            for key, value in missing.items()
            if value > 0
        },
        "infinite_values": {
            key: int(value)
            for key, value in infinite.items()
            if value > 0
        },
        "constant_columns": constant,
        "data_types": {
            key: str(value)
            for key, value in df.dtypes.items()
        },
        "target_distribution": (
            {
                str(key): int(value)
                for key, value in df[target]
                .value_counts(dropna=False).items()
            }
            if target in df.columns
            else None
        ),
    }

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/dataset_ml_1day.csv"
    )
    parser.add_argument("--target", default="target")
    parser.add_argument(
        "--output",
        default="reports/data_quality.json"
    )
    args = parser.parse_args()

    input_path = ROOT / args.input
    output_path = ROOT / args.output

    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    result = validate_data(input_path, args.target)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nRelatório salvo em: {output_path}")


if __name__ == "__main__":
    main()