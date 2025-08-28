import asyncio
from httpx import ASGITransport, AsyncClient

from reputeai.app.main import app
from reputeai.app.db.base import Base
from reputeai.app.db.session import engine


def test_login_rate_limit():
    Base.metadata.create_all(bind=engine)

    async def _flow():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for _ in range(5):
                await client.post("/auth/login", json={"email": "a@b.c", "password": "bad"})
            return await client.post("/auth/login", json={"email": "a@b.c", "password": "bad"})

    resp = asyncio.run(_flow())
    assert resp.status_code == 429
