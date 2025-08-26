from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models import Membership, Org, OrgRole, User
from ..core.security import decode_token
from ..core.config import settings


async def get_current_user(
    token: str | None = Header(None, alias="Authorization"),
    access_token_cookie: str | None = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db),
) -> User:
    if settings.use_cookies:
        token = access_token_cookie
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if token.lower().startswith("bearer "):
        token = token[7:]
    payload = decode_token(token)
    user_id = int(payload.get("sub"))
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


def get_current_org(required_role: OrgRole | None = None):
    async def dep(
        x_org_id: int = Header(..., alias="X-Org-Id"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Org:
        membership = (
            db.query(Membership)
            .filter(Membership.user_id == current_user.id, Membership.org_id == x_org_id)
            .first()
        )
        if not membership:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")
        if required_role and membership.role not in {required_role, OrgRole.owner}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        org = db.get(Org, x_org_id)
        if org is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Org not found")
        return org

    return dep
