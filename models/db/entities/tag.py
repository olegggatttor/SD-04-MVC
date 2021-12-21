from sqlalchemy import Column, Integer, String

from utils.constants import MAX_LOGIN_LENGTH
from models.db.database import Base


class Tag(Base):
    __tablename__ = "Tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(String(MAX_LOGIN_LENGTH), nullable=False)
    tag_name = Column(String(100))
    usage_counter = Column(Integer, nullable=False)
