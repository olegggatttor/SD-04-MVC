from sqlalchemy.orm import Session

from models.db.entities.user import User
from sqlalchemy.orm.exc import NoResultFound


class UserManager:
    @staticmethod
    def get_user_credentials(db: Session, login: str):
        try:
            user = db.query(User).filter_by(login=login).one()
            return user
        except NoResultFound:
            return None

    @staticmethod
    def user_exists(db: Session, login: str) -> bool:
        return UserManager.get_user_credentials(db, login) is not None

    @staticmethod
    def add_new_user(db: Session, login: str, password: str):
        db.add(User(login=login, password=password))
        db.commit()
