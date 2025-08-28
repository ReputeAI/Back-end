from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReplyCreate(BaseModel):
    text: str
    is_auto: bool = False


class ReplyOut(BaseModel):
    id: int
    org_id: int
    review_id: int
    text: str
    is_auto: bool
    status: str
    platform_status: str | None = None
    posted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
