from pydantic import BaseModel


class TaskList(BaseModel):
    id: int
    board_id: int
    owner_id: str
    task_list_name: str
    tags: set

    class Config:
        orm_mode = True
