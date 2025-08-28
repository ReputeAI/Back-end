from datetime import datetime, time

from pydantic import BaseModel


class AutoReplySimulateRequest(BaseModel):
    rating: int
    text: str
    timestamp: datetime
    min_rating: int = 4
    blacklist: list[str] = []
    office_hours_start: time = time(9, 0)
    office_hours_end: time = time(17, 0)


class AutoReplySimulateResponse(BaseModel):
    eligible: bool
