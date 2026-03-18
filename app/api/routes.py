from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from app.agents.agent import EnterpriseCopilotAgent
from app.evaluation.datasets import GoldenDataset
from app.evaluation.evaluator import evaluate_run
from app.security.auth import AuthUser, create_access_token, get_current_user, require_roles
from app.ui.templates import dashboard_html, index_html

router = APIRouter()
agent = EnterpriseCopilotAgent()


class ChatRequest(BaseModel):
    question: str


class EvalRequest(BaseModel):
    run_name: str = "local-eval"


@router.get("/", response_class=HTMLResponse)
async def home() -> str:
    return index_html()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    return dashboard_html()


@router.get("/auth/demo-token")
async def demo_token(user_id: str = "demo-user", roles: str = "analyst") -> dict:
    parsed_roles = [r.strip() for r in roles.split(",") if r.strip()]
    token = create_access_token(user_id=user_id, roles=parsed_roles)
    return {"access_token": token, "token_type": "bearer", "roles": parsed_roles}


@router.post("/chat")
async def chat(
    req: ChatRequest,
    user: Annotated[AuthUser, Depends(require_roles(["viewer", "analyst", "operator", "admin"]))],
) -> dict:
    result = await agent.run(question=req.question, user_id=user.user_id, roles=user.roles)
    return result


@router.post("/chat/stream")
async def chat_stream(
    req: ChatRequest,
    user: Annotated[AuthUser, Depends(require_roles(["viewer", "analyst", "operator", "admin"]))],
) -> StreamingResponse:
    stream = agent.stream(question=req.question, user_id=user.user_id, roles=user.roles)
    return StreamingResponse(stream, media_type="text/plain")


@router.post("/evaluate")
async def evaluate(
    req: EvalRequest,
    user: Annotated[AuthUser, Depends(require_roles(["admin"]))],
) -> dict:
    dataset = GoldenDataset.default_samples()
    summary = await evaluate_run(agent=agent, samples=dataset, run_name=req.run_name)
    return summary


@router.get("/auth/me")
async def auth_me(user: Annotated[AuthUser, Depends(get_current_user)]) -> dict:
    return {"user_id": user.user_id, "roles": user.roles}
