from fastapi import FastAPI

from .api.routes import router

app = FastAPI(title="ReputeAI Backend")
app.include_router(router)


@app.get('/', tags=['health'])
async def root() -> dict[str, str]:
    return {"message": "ReputeAI backend running"}
