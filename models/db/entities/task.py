from sqlalchemy import Column, Integer, String, Boolean, PickleType

from utils.constants import MAX_LOGIN_LENGTH
from models.db.database import Base


class Task(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    board_id = Column(Integer, nullable=False)
    task_list_id = Column(Integer)
    owner_id = Column(String(MAX_LOGIN_LENGTH), nullable=False)
    task_name = Column(String(100))
    task_desc = Column(String(255))
    is_done = Column(Boolean)
    pipeline_id = Column(Integer, nullable=False)
    cur_pipeline_index = Column(Integer, nullable=False)
    tags = Column(PickleType)
