from pydantic import BaseModel, ConfigDict, EmailStr

from ..models.membership import OrgRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Membership(BaseModel):
    org_id: int
    role: OrgRole

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserMe(User):
    memberships: list[Membership] = []
