from pydantic import BaseModel


class SentimentRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    label: str
    confidence: float
    aspects: list[str]


class SuggestReplyRequest(BaseModel):
    review_id: int
    tone: str | None = None
    language: str | None = None


class SuggestReplyResponse(BaseModel):
    suggestions: list[str]


class BatchSuggestRequest(BaseModel):
    review_ids: list[int]

