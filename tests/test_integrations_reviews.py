import asyncio
import pytest
from httpx import ASGITransport, AsyncClient

from reputeai.app.main import app
from reputeai.app.db.base import Base
from reputeai.app.db.session import engine


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_integration_and_reviews_flow():
    async def _flow():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/orgs/1/integrations/google/connect")
            assert resp.status_code == 200
            assert "google" in resp.json()["authorization_url"]

            resp = await client.get("/integrations/google/callback", params={"code": "abc", "state": 1})
            assert resp.status_code == 200

            resp = await client.get("/integrations/")
            assert resp.status_code == 200
            assert len(resp.json()) == 1

            resp = await client.post("/orgs/1/reviews/refresh")
            assert resp.status_code == 200

            resp = await client.get("/orgs/1/reviews")
            assert resp.status_code == 200
            reviews = resp.json()
            assert len(reviews) == 1
            assert reviews[0]["platform"] == "google"

            await client.post("/orgs/1/reviews/refresh")
            resp = await client.get("/orgs/1/reviews")
            assert len(resp.json()) == 1

            resp = await client.get("/orgs/1/reviews", params={"q": "Great"})
            assert len(resp.json()) == 1

    asyncio.run(_flow())
