from pydantic import BaseModel


class Task(BaseModel):
    id: int
    board_id: int
    task_list_id: int
    owner_id: str
    task_name: str
    task_desc: str
    is_done: bool
    pipeline_id: int
    tags: set

    class Config:
        orm_mode = True
