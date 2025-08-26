from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_current_user
from ..db.session import get_db
from ..models import Membership
from ..schemas.user import Membership as MembershipSchema, UserMe

router = APIRouter()


@router.get("/me", response_model=UserMe)
async def read_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)) -> UserMe:
    memberships = (
        db.query(Membership).filter(Membership.user_id == current_user.id).all()
    )
    membership_models = [MembershipSchema.model_validate(m) for m in memberships]
    return UserMe(
        id=current_user.id,
        email=current_user.email,
        is_verified=current_user.is_verified,
        memberships=membership_models,
    )
