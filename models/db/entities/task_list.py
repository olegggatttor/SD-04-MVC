from sqlalchemy import Column, Integer, String, PickleType

from utils.constants import MAX_LOGIN_LENGTH
from models.db.database import Base


class TaskList(Base):
    __tablename__ = "TaskLists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    board_id = Column(Integer, nullable=False)
    owner_id = Column(String(MAX_LOGIN_LENGTH), nullable=False)
    task_list_name = Column(String(100))
    tags = Column(PickleType)
