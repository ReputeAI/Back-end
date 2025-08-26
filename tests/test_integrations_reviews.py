from fastapi.testclient import TestClient
import pytest

import pytest
from fastapi.testclient import TestClient

from reputeai.app.main import app
from reputeai.app.db.base import Base
from reputeai.app.db.session import engine


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_integration_and_reviews_flow():
    resp = client.post("/orgs/1/integrations/google/connect")
    assert resp.status_code == 200
    assert "google" in resp.json()["authorization_url"]

    resp = client.get("/integrations/google/callback", params={"code": "abc", "state": 1})
    assert resp.status_code == 200

    resp = client.get("/integrations")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.post("/orgs/1/reviews/refresh")
    assert resp.status_code == 200

    resp = client.get("/orgs/1/reviews")
    assert resp.status_code == 200
    reviews = resp.json()
    assert len(reviews) == 1
    assert reviews[0]["platform"] == "google"

    client.post("/orgs/1/reviews/refresh")
    resp = client.get("/orgs/1/reviews")
    assert len(resp.json()) == 1

    resp = client.get("/orgs/1/reviews", params={"q": "Great"})
    assert len(resp.json()) == 1
