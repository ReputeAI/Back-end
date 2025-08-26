from pydantic import BaseModel, ConfigDict


class Usage(BaseModel):
    id: int
    units: int

    model_config = ConfigDict(from_attributes=True)
