from sqlalchemy import Column, Integer, String, PickleType

from utils.constants import MAX_LOGIN_LENGTH
from models.db.database import Base


class Pipeline(Base):
    __tablename__ = "Pipelines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(String(MAX_LOGIN_LENGTH), nullable=False)
    pipeline_name = Column(String(100))
    pipeline = Column(PickleType)
