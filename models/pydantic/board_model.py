from pydantic import BaseModel


class Board(BaseModel):
    id: int
    owner_id: str
    board_name: str

    class Config:
        orm_mode = True
