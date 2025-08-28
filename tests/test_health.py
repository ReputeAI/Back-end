import asyncio
from httpx import ASGITransport, AsyncClient

from reputeai.app.main import app


def test_health():
    async def _call():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/health")

    resp = asyncio.run(_call())
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
