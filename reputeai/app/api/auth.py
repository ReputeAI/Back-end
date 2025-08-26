from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.rate_limit import limiter
from ..db.session import get_db
from ..dependencies import get_current_user
from ..schemas.auth import LoginRequest, TokenPair
from ..schemas.user import UserCreate
from ..services.auth import AuthService

router = APIRouter(prefix="/auth")
auth_service = AuthService()


def _extract_token(
    refresh_token_cookie: str | None,
    refresh_header: str | None,
) -> str | None:
    token = None
    if settings.use_cookies:
        token = refresh_token_cookie
    else:
        token = refresh_header
        if token and token.lower().startswith("bearer "):
            token = token[7:]
    return token


@router.post("/register", response_model=TokenPair)
@limiter.limit("10/minute")
def register(data: UserCreate, response: Response, db: Session = Depends(get_db)) -> TokenPair:
    user = auth_service.register_user(db, data.email, data.password)
    access, refresh = auth_service.create_tokens(db, user)
    if settings.use_cookies:
        response.set_cookie("access_token", access, httponly=True)
        response.set_cookie("refresh_token", refresh, httponly=True)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPair)
@limiter.limit("10/minute")
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)) -> TokenPair:
    user = auth_service.authenticate(db, data.email, data.password)
    access, refresh = auth_service.create_tokens(db, user)
    if settings.use_cookies:
        response.set_cookie("access_token", access, httponly=True)
        response.set_cookie("refresh_token", refresh, httponly=True)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("10/minute")
def refresh(
    response: Response,
    refresh_token_cookie: str | None = Cookie(None, alias="refresh_token"),
    refresh_header: str | None = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> TokenPair:
    token = _extract_token(refresh_token_cookie, refresh_header)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    access, refresh = auth_service.refresh(db, token)
    if settings.use_cookies:
        response.set_cookie("access_token", access, httponly=True)
        response.set_cookie("refresh_token", refresh, httponly=True)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/logout")
@limiter.limit("10/minute")
def logout(
    response: Response,
    refresh_token_cookie: str | None = Cookie(None, alias="refresh_token"),
    refresh_header: str | None = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> dict:
    token = _extract_token(refresh_token_cookie, refresh_header)
    if token:
        auth_service.logout(db, token)
    if settings.use_cookies:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
    return {"status": "logged out"}


@router.post("/verify-email")
@limiter.limit("10/minute")
def verify_email(current_user=Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    current_user.is_verified = True
    db.commit()
    return {"status": "verified"}


@router.post("/forgot-password")
@limiter.limit("10/minute")
def forgot_password() -> dict:
    return {"status": "ok"}


@router.post("/reset-password")
@limiter.limit("10/minute")
def reset_password() -> dict:
    return {"status": "ok"}


@router.get("/oidc/start")
@limiter.limit("10/minute")
def oidc_start() -> dict:
    return {"url": "https://accounts.google.com/o/oauth2/v2/auth"}


@router.get("/oidc/callback")
@limiter.limit("10/minute")
def oidc_callback() -> dict:
    return {"status": "oidc callback"}
