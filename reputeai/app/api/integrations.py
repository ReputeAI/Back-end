from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.integration import Integration
from ..services.integrations import get_provider
from ..core.security import encrypt_token
from ..services.usage import log_usage

router = APIRouter(prefix="/integrations")


@router.get("/", response_model=None)
def list_integrations(db: Session = Depends(get_db)):
    return db.query(Integration).all()


@router.get("/{provider}/callback")
def oauth_callback(
    provider: str,
    code: str,
    state: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        provider_impl = get_provider(provider)
    except KeyError as exc:  # pragma: no cover - invalid provider
        raise HTTPException(status_code=404, detail="Unknown provider") from exc

    token_data = provider_impl.exchange_code(code)
    existing = (
        db.query(Integration)
        .filter(Integration.org_id == state, Integration.provider == provider)
        .first()
    )
    if not existing:
        log_usage(db, state, "connected_locations")
    db.merge(
        Integration(
            org_id=state,
            provider=provider,
            access_token=encrypt_token(token_data["access_token"]),
            refresh_token=encrypt_token(token_data.get("refresh_token", "")),
            expires_at=token_data.get("expires_at", datetime.utcnow()),
            meta=token_data.get("metadata", {}),
        )
    )
    db.commit()
    return {"status": "ok"}
