import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def analyze_features(input_path, target):
    df = pd.read_csv(input_path)

    if target not in df.columns:
        raise ValueError(f"Target não encontrado: {target}")

    features = df.drop(columns=[target]).select_dtypes(
        include="number"
    )

    if features.empty:
        raise ValueError("Nenhuma variável numérica encontrada.")

    summaries = []

    for column in features.columns:
        for class_value, group in df.groupby(
            target,
            dropna=False,
            observed=True
        ):
            values = pd.to_numeric(
                group[column],
                errors="coerce"
            ).dropna()

            if values.empty:
                continue

            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1

            if iqr == 0:
                outliers = 0
            else:
                outliers = int(
                    ((values < q1 - 1.5 * iqr) |
                     (values > q3 + 1.5 * iqr)).sum()
                )

            summaries.append({
                "feature": column,
                "target_class": str(class_value),
                "count": int(values.count()),
                "mean": float(values.mean()),
                "median": float(values.median()),
                "std": float(values.std()) if len(values) > 1 else 0.0,
                "min": float(values.min()),
                "q25": float(q1),
                "q75": float(q3),
                "max": float(values.max()),
                "outlier_count_iqr": outliers,
                "outlier_pct_iqr": round(
                    outliers / len(values) * 100, 2
                ),
            })

    return pd.DataFrame(summaries)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/dataset_ml_1day.csv"
    )
    parser.add_argument("--target", default="target")
    parser.add_argument(
        "--output",
        default="reports/feature_analysis.csv"
    )
    args = parser.parse_args()

    input_path = ROOT / args.input
    output_path = ROOT / args.output

    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    result = analyze_features(input_path, args.target)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    print(result.to_string(index=False))
    print(f"\nRelatório salvo em: {output_path}")


if __name__ == "__main__":
    main()