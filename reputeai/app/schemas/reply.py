from pydantic import BaseModel, ConfigDict


class Reply(BaseModel):
    id: int
    message: str

    model_config = ConfigDict(from_attributes=True)
