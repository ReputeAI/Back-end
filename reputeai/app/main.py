from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from .api.auth import router as auth_router
from .api.users import router as users_router
from .api.integrations import router as integrations_router
from .api.orgs import router as orgs_router
from .api.ai import router as ai_router
from .api.billing import router as billing_router
from .api.usage import router as usage_router
from .api.webhooks import router as webhooks_router
from .core.config import settings
from .core.logging import configure_logging
from .core.rate_limit import limiter
from .core.middleware import CorrelationIdMiddleware, SecurityHeadersMiddleware

configure_logging()
app = FastAPI(
    title="ReputeAI Backend",
    description="APIs for auth, tweets, etc.",
    version="0.1.0",                 # shows in docs
    docs_url="/docs",                # Swagger UI
    redoc_url="/redoc",              # ReDoc
    openapi_url="/openapi.json",     # OpenAPI spec URL
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(integrations_router)
app.include_router(orgs_router)
app.include_router(ai_router)
app.include_router(billing_router)
app.include_router(usage_router)
app.include_router(webhooks_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
