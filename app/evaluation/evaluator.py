from __future__ import annotations

import mlflow

from app.core.config import settings
from app.evaluation.datasets import GoldenSample


def _score_answer(answer: str, expected_keywords: list[str]) -> tuple[float, float]:
    lower_answer = answer.lower()
    matched = [kw for kw in expected_keywords if kw.lower() in lower_answer]

    precision = len(matched) / max(1, len(set(answer.lower().split())))
    recall = len(matched) / max(1, len(expected_keywords))
    return precision, recall


async def evaluate_run(agent, samples: list[GoldenSample], run_name: str) -> dict:
    if settings.mlflow_tracking_uri:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)

    rows: list[dict] = []
    for i, sample in enumerate(samples):
        result = await agent.run(question=sample.question, user_id="evaluator", roles=["admin"])
        precision, recall = _score_answer(result["answer"], sample.expected_keywords)
        rows.append(
            {
                "id": i,
                "question": sample.question,
                "precision": precision,
                "recall": recall,
                "trace_id": result["trace_id"],
            }
        )

    avg_precision = sum(r["precision"] for r in rows) / max(1, len(rows))
    avg_recall = sum(r["recall"] for r in rows) / max(1, len(rows))

    with mlflow.start_run(run_name=run_name):
        mlflow.log_metric("avg_precision", avg_precision)
        mlflow.log_metric("avg_recall", avg_recall)
        mlflow.log_text(str(rows), artifact_file="evaluation/results.txt")

    return {
        "run_name": run_name,
        "avg_precision": avg_precision,
        "avg_recall": avg_recall,
        "rows": rows,
    }
