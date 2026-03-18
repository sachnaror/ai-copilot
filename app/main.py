from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

app = FastAPI(title="Enterprise AI Knowledge Copilot", version="1.0.0")
app.include_router(router)
app.mount("/ui", StaticFiles(directory="app/ui", html=True), name="ui")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
