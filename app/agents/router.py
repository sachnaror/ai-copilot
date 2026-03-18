from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agents import tools


@dataclass
class ToolDecision:
    tool_name: str
    args: dict[str, Any]
    reason: str


class MCPStyleToolRouter:
    """Simple intent router representing MCP-style orchestration semantics."""

    def route(self, question: str) -> ToolDecision | None:
        q = question.lower()
        if "jira" in q or "ticket" in q:
            return ToolDecision(
                tool_name="fetch_jira_tickets",
                args={"project_key": "ENG"},
                reason="Question asks about issue tracking details.",
            )
        if "sql" in q or "database" in q or "revenue" in q:
            return ToolDecision(
                tool_name="run_sql_query",
                args={"sql": "SELECT NOW() AS ts"},
                reason="Question appears data/analytics oriented.",
            )
        if "trigger" in q or "api" in q:
            return ToolDecision(
                tool_name="trigger_internal_api",
                args={"api_name": "incident_webhook", "body": {"source": "copilot"}},
                reason="Question requests operational API action.",
            )
        return None

    def execute(self, decision: ToolDecision) -> dict[str, Any]:
        if decision.tool_name == "fetch_jira_tickets":
            return tools.fetch_jira_tickets(**decision.args)
        if decision.tool_name == "run_sql_query":
            return tools.run_sql_query(**decision.args)
        if decision.tool_name == "trigger_internal_api":
            return tools.trigger_internal_api(**decision.args)
        raise ValueError(f"Unsupported tool: {decision.tool_name}")
