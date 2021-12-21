from pydantic import BaseModel


class Tag(BaseModel):
    id: int
    owner_id: str
    tag_name: str
    usage_counter: int

    class Config:
        orm_mode = True
