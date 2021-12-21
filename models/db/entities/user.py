from sqlalchemy import Column, String

from utils.constants import MAX_LOGIN_LENGTH, MAX_PASSWORD_LENGTH
from models.db.database import Base


class User(Base):
    __tablename__ = "Users"

    login = Column(String(MAX_LOGIN_LENGTH), primary_key=True, nullable=False)
    password = Column(String(MAX_PASSWORD_LENGTH), nullable=False)
