import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_report(path):
    if not path.is_file():
        return None

    return json.loads(path.read_text(encoding="utf-8"))


def build_report(reports_dir):
    quality = load_report(reports_dir / "data_quality.json")
    temporal = load_report(reports_dir / "temporal_validation.json")
    evaluation = load_report(reports_dir / "model_evaluation.json")

    lines = [
        "# Relatório de diagnóstico",
        "",
        f"Gerado em: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]

    if quality:
        lines.extend([
            "## Qualidade dos dados",
            "",
            f"- Registros: {quality['rows']}",
            f"- Colunas: {quality['columns']}",
            f"- Linhas duplicadas: {quality['duplicate_rows']}",
            f"- Colunas constantes: {len(quality['constant_columns'])}",
            f"- Colunas com valores ausentes: {len(quality['missing_values'])}",
            f"- Colunas com infinitos: {len(quality['infinite_values'])}",
            "",
        ])
    else:
        lines.extend([
            "## Qualidade dos dados",
            "",
            "Relatório ainda não disponível.",
            "",
        ])

    if temporal:
        lines.extend([
            "## Validação temporal",
            "",
            f"- Coluna analisada: {temporal['time_column']}",
            f"- Timestamps inválidos: {temporal['invalid_timestamps']}",
            f"- Timestamps duplicados: {temporal['duplicate_timestamps']}",
            f"- Ordem estritamente crescente: {temporal['strictly_increasing']}",
            f"- Intervalos suspeitos: {temporal['missing_intervals_detected']}",
            "",
        ])
    else:
        lines.extend([
            "## Validação temporal",
            "",
            "Relatório ainda não disponível.",
            "",
        ])

    if evaluation:
        lines.extend([
            "## Avaliação do modelo",
            "",
            f"- Registros avaliados: {evaluation['rows_evaluated']}",
            f"- Acurácia: {evaluation['accuracy']:.4f}",
            f"- Acurácia balanceada: {evaluation['balanced_accuracy']:.4f}",
            "",
            "### Métricas por classe",
            "",
            "| Classe | Precision | Recall | F1-score |",
            "|---|---:|---:|---:|",
        ])

        for label in evaluation["labels"]:
            metrics = evaluation["classification_report"].get(label)

            if isinstance(metrics, dict):
                lines.append(
                    f"| {label} | "
                    f"{metrics['precision']:.4f} | "
                    f"{metrics['recall']:.4f} | "
                    f"{metrics['f1-score']:.4f} |"
                )

        lines.append("")
    else:
        lines.extend([
            "## Avaliação do modelo",
            "",
            "Relatório ainda não disponível.",
            "",
        ])

    feature_path = reports_dir / "feature_analysis.csv"

    lines.extend([
        "## Análise das variáveis",
        "",
        (
            f"Relatório disponível: `{feature_path.name}`."
            if feature_path.is_file()
            else "Relatório ainda não disponível."
        ),
        "",
        "## Próximas ações",
        "",
        "- Investigar problemas de qualidade identificados.",
        "- Analisar diferenças entre as classes.",
        "- Validar a separação temporal entre treino e teste.",
        "- Interpretar as métricas conforme o objetivo de negócio.",
        "- Não alterar o conjunto de teste para melhorar os resultados.",
    ])

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument(
        "--output",
        default="reports/diagnostic_report.md"
    )
    args = parser.parse_args()

    reports_dir = ROOT / args.reports_dir
    output_path = ROOT / args.output

    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = build_report(reports_dir)
    output_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nRelatório salvo em: {output_path}")


if __name__ == "__main__":
    main()