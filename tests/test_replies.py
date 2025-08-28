import asyncio
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from reputeai.app.main import app
from reputeai.app.db.base import Base
from reputeai.app.db.session import engine, SessionLocal
from reputeai.app.models import Org, Integration, Review, AuditLog


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def seed_data() -> None:
    with SessionLocal() as db:
        org = Org(id=1, name="Test")
        integration = Integration(org_id=1, provider="google", access_token="token")
        review = Review(
            id=1,
            org_id=1,
            platform="google",
            external_id="r1",
            text="Great",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add_all([org, integration, review])
        db.commit()


def test_reply_workflow():
    seed_data()

    async def _flow():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/orgs/1/reviews/1/reply", json={"text": "Thanks", "is_auto": False})
            assert resp.status_code == 200
            reply = resp.json()
            assert reply["status"] == "draft"

            resp = await client.post("/orgs/1/reviews/1/send-reply")
            assert resp.status_code == 200
            sent = resp.json()
            assert sent["status"] == "sent"

            resp = await client.get("/orgs/1/replies", params={"review_id": 1})
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 1

    asyncio.run(_flow())

    with SessionLocal() as db:
        logs = db.query(AuditLog).all()
        assert len(logs) == 2


def test_autoreply_simulation():
    async def _flow():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/orgs/1/autoreply/simulate",
                json={
                    "rating": 5,
                    "text": "Great service",
                    "timestamp": "2024-01-01T10:00:00",
                    "min_rating": 4,
                    "blacklist": ["bad"],
                    "office_hours_start": "09:00",
                    "office_hours_end": "17:00",
                },
            )
            assert resp.status_code == 200
            assert resp.json()["eligible"] is True

            resp = await client.post(
                "/orgs/1/autoreply/simulate",
                json={
                    "rating": 3,
                    "text": "Great service",
                    "timestamp": "2024-01-01T10:00:00",
                    "min_rating": 4,
                    "blacklist": [],
                    "office_hours_start": "09:00",
                    "office_hours_end": "17:00",
                },
            )
            assert resp.json()["eligible"] is False

    asyncio.run(_flow())
