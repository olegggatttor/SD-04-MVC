from pydantic import BaseModel


class Pipeline(BaseModel):
    id: int
    owner_id: str
    pipeline_name: str
    pipeline: list

    class Config:
        orm_mode = True
