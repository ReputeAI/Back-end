from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Provider(Protocol):
    name: str

    def get_authorization_url(self, org_id: int) -> str:
        ...

    def exchange_code(self, code: str) -> dict[str, Any]:
        ...

    def fetch_reviews(self, token: str, since: datetime | None = None) -> list[dict[str, Any]]:
        ...


_providers: dict[str, Provider] = {}


def register(provider: Provider) -> None:
    _providers[provider.name] = provider


def get_provider(name: str) -> Provider:
    return _providers[name]


@dataclass
class DummyProvider:
    name: str

    def get_authorization_url(self, org_id: int) -> str:
        return f"https://auth.example.com/{self.name}?state={org_id}"

    def exchange_code(self, code: str) -> dict[str, Any]:
        return {
            "access_token": f"{self.name}-{code}-token",
            "refresh_token": f"{self.name}-{code}-refresh",
            "expires_at": datetime.utcnow() + timedelta(hours=1),
            "metadata": {},
        }

    def fetch_reviews(self, token: str, since: datetime | None = None) -> list[dict[str, Any]]:
        return [
            {
                "external_id": "1",
                "platform": self.name,
                "author": "Alice",
                "rating": 5,
                "text": f"Great service from {self.name}!",
                "lang": "en",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "metadata": {},
            }
        ]


# Register default providers
register(DummyProvider("google"))
register(DummyProvider("trustpilot"))
