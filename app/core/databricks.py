from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import requests

from app.core.config import settings


@dataclass
class RetrievalResult:
    source: str
    content: str
    score: float


class DatabricksClient:
    """Databricks REST integration with local-safe fallback mode."""

    def __init__(self) -> None:
        self.host = (settings.databricks_host or settings.databricks_workspace_url).rstrip("/")
        self.token = settings.databricks_token
        self.timeout_seconds = 30

    @property
    def enabled(self) -> bool:
        return bool(self.host and self.token)

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.host}{path}"
        resp = requests.post(url, headers=self._headers, json=payload, timeout=self.timeout_seconds)
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str) -> dict[str, Any]:
        url = f"{self.host}{path}"
        resp = requests.get(url, headers=self._headers, timeout=self.timeout_seconds)
        resp.raise_for_status()
        return resp.json()

    def vector_search(self, query: str, k: int = 4) -> list[RetrievalResult]:
        if not self.enabled or not settings.databricks_vector_search_index:
            return self._mock_vector_search()

        payload = {
            "query_text": query,
            "num_results": k,
        }

        # Databricks Vector Search REST endpoint.
        try:
            data = self._post(
                f"/api/2.0/vector-search/indexes/{settings.databricks_vector_search_index}/query",
                payload,
            )
        except requests.RequestException:
            return self._mock_vector_search()

        docs = data.get("result", {}).get("data_array", [])
        results: list[RetrievalResult] = []
        for row in docs:
            source = str(row[0]) if len(row) > 0 else "databricks://unknown"
            content = str(row[1]) if len(row) > 1 else ""
            score = float(row[-1]) if row else 0.0
            results.append(RetrievalResult(source=source, content=content, score=score))

        return results or self._mock_vector_search()

    def invoke_model(self, prompt: str, context: list[str]) -> str:
        if not self.enabled or not settings.databricks_model_serving_endpoint:
            return self._mock_model_response(prompt, context)

        system_prompt = (
            "You are an enterprise knowledge copilot. Answer grounded in context and tool outputs. "
            "If unknown, say you are not sure."
        )
        joined_context = "\n\n".join(context[:6])

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{joined_context}\n\nQuestion: {prompt}"},
            ],
            "max_tokens": 500,
            "temperature": 0.1,
        }

        try:
            data = self._post(
                f"/serving-endpoints/{settings.databricks_model_serving_endpoint}/invocations",
                payload,
            )
        except requests.RequestException:
            return self._mock_model_response(prompt, context)

        choices = data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if content:
                return str(content)

        predictions = data.get("predictions")
        if isinstance(predictions, list) and predictions:
            return str(predictions[0])

        return json.dumps(data)

    def run_uc_function(self, function_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled or not settings.databricks_sql_warehouse_id:
            return {
                "function": function_name,
                "payload": payload,
                "status": "mock-ok",
                "result": {"note": "Set DATABRICKS_SQL_WAREHOUSE_ID for real UC function execution."},
            }

        payload_json = json.dumps(payload).replace("'", "''")
        sql = f"SELECT {function_name}('{payload_json}') AS result"

        try:
            create = self._post(
                "/api/2.0/sql/statements",
                {
                    "statement": sql,
                    "warehouse_id": settings.databricks_sql_warehouse_id,
                    "wait_timeout": "10s",
                    "disposition": "INLINE",
                },
            )
        except requests.RequestException as exc:
            return {
                "function": function_name,
                "payload": payload,
                "status": "error",
                "error": str(exc),
            }

        statement_id = create.get("statement_id")
        if not statement_id:
            return {"function": function_name, "payload": payload, "status": "error", "raw": create}

        for _ in range(12):
            try:
                data = self._get(f"/api/2.0/sql/statements/{statement_id}")
            except requests.RequestException as exc:
                return {
                    "function": function_name,
                    "payload": payload,
                    "status": "error",
                    "statement_id": statement_id,
                    "error": str(exc),
                }
            state = data.get("status", {}).get("state")
            if state == "SUCCEEDED":
                rows = data.get("result", {}).get("data_array", [])
                value = rows[0][0] if rows and rows[0] else None
                return {
                    "function": function_name,
                    "payload": payload,
                    "status": "succeeded",
                    "result": value,
                    "statement_id": statement_id,
                }
            if state in {"FAILED", "CANCELED", "CLOSED"}:
                return {
                    "function": function_name,
                    "payload": payload,
                    "status": state.lower(),
                    "statement_id": statement_id,
                    "error": data,
                }
            time.sleep(1)

        return {
            "function": function_name,
            "payload": payload,
            "status": "timeout",
            "statement_id": statement_id,
        }

    @staticmethod
    def _mock_vector_search() -> list[RetrievalResult]:
        return [
            RetrievalResult(
                source="mock://policy.pdf",
                content=(
                    "Internal policy says customer-facing incidents must be updated in Jira "
                    "every 30 minutes until resolved."
                ),
                score=0.83,
            ),
            RetrievalResult(
                source="mock://slack-thread",
                content="SRE handoff checklist includes rollback, owner assignment, and stakeholder update.",
                score=0.79,
            ),
        ]

    @staticmethod
    def _mock_model_response(prompt: str, context: list[str]) -> str:
        ctx = " | ".join(context[:2])
        return f"[Mock Mosaic Response] {prompt}\n\nContext: {ctx}"
