from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import mlflow

from app.core.config import settings


class MLflowLogger:
    def __init__(self) -> None:
        if settings.mlflow_tracking_uri:
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment_name)
        self.local_trace_dir = Path("logs")
        self.local_trace_dir.mkdir(exist_ok=True)

    def log_chat(
        self,
        user_id: str,
        question: str,
        answer: str,
        retrieved: list[dict[str, Any]],
        tool_output: dict[str, Any] | None,
    ) -> str:
        trace_id = str(uuid.uuid4())
        with mlflow.start_run(run_name="chat-turn", nested=True):
            mlflow.log_param("user_id", user_id)
            mlflow.log_param("trace_id", trace_id)
            mlflow.log_param("question", question[:500])
            mlflow.log_metric("retrieved_chunks", float(len(retrieved)))
            mlflow.log_text(answer, artifact_file=f"answers/{trace_id}.txt")
            mlflow.log_text(json.dumps(retrieved, indent=2), artifact_file=f"retrieval/{trace_id}.json")
            if tool_output is not None:
                mlflow.log_text(json.dumps(tool_output, indent=2), artifact_file=f"tools/{trace_id}.json")

        local_payload = {
            "trace_id": trace_id,
            "ts": int(time.time()),
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "retrieved": retrieved,
            "tool_output": tool_output,
        }
        (self.local_trace_dir / f"{trace_id}.json").write_text(json.dumps(local_payload, indent=2), encoding="utf-8")
        return trace_id
