from fastapi import FastAPI
from .core.logging import configure_logging
from .core.rate_limit import limiter
from slowapi.middleware import SlowAPIMiddleware

configure_logging()
app = FastAPI()

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
