from __future__ import annotations

from collections.abc import AsyncGenerator

from app.agents.router import MCPStyleToolRouter
from app.agents.tools import allowed_tools_for_roles
from app.core.databricks import DatabricksClient
from app.core.streaming import token_stream
from app.evaluation.mlflow_logger import MLflowLogger
from app.rag.retriever import EnterpriseRetriever


class EnterpriseCopilotAgent:
    def __init__(self) -> None:
        self.retriever = EnterpriseRetriever()
        self.router = MCPStyleToolRouter()
        self.dbx = DatabricksClient()
        self.logger = MLflowLogger()

    async def run(self, question: str, user_id: str, roles: list[str]) -> dict:
        retrieved = self.retriever.retrieve(question)
        context = [item.content for item in retrieved]

        tool_output = None
        decision = self.router.route(question)
        allowed = allowed_tools_for_roles(roles)
        if decision:
            if decision.tool_name in allowed:
                tool_output = self.router.execute(decision)
                context.append(f"Tool output: {tool_output}")
            else:
                tool_output = {
                    "status": "denied",
                    "tool": decision.tool_name,
                    "reason": f"Role does not allow tool '{decision.tool_name}'",
                }
                context.append(f"Tool denied: {tool_output}")

        answer = self.dbx.invoke_model(prompt=question, context=context)

        trace_id = self.logger.log_chat(
            user_id=user_id,
            question=question,
            answer=answer,
            retrieved=[r.__dict__ for r in retrieved],
            tool_output=tool_output,
        )

        return {
            "answer": answer,
            "trace_id": trace_id,
            "retrieved": [r.__dict__ for r in retrieved],
            "tool_output": tool_output,
            "roles": roles,
        }

    async def stream(self, question: str, user_id: str, roles: list[str]) -> AsyncGenerator[str, None]:
        result = await self.run(question=question, user_id=user_id, roles=roles)
        async for token in token_stream(result["answer"]):
            yield token
