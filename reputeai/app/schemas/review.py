from pydantic import BaseModel, ConfigDict


class Review(BaseModel):
    id: int
    content: str

    model_config = ConfigDict(from_attributes=True)
