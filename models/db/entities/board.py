from sqlalchemy import Column, Integer, String

from utils.constants import MAX_LOGIN_LENGTH
from models.db.database import Base


class Board(Base):
    __tablename__ = "Boards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(String(MAX_LOGIN_LENGTH), nullable=False)
    board_name = Column(String(100))
