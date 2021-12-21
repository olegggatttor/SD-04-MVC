from sqlalchemy.orm import Session

from exceptions.custom_exceptions import TagDoesNotExistException, TagIsUsedException
from models.db.entities.tag import Tag


class TagManager:
    @staticmethod
    def assert_tag_exists(db: Session, tag_id: int, login: str):
        return db.query(Tag).filter_by(id=tag_id, owner_id=login).scalar()

    @staticmethod
    def assert_tag_is_not_used(db: Session, tag_id: int, login: str):
        return db.query(Tag).filter_by(id=tag_id, owner_id=login).one().usage_counter == 0

    @staticmethod
    def get_all_tags_for_user(db: Session, username: str):
        tags = db.query(Tag).filter_by(owner_id=username).all()
        return tags

    @staticmethod
    def add_tag(db: Session, tag_name: str, login: str):
        db.add(Tag(tag_name=tag_name, owner_id=login, usage_counter=0))
        db.commit()

    @staticmethod
    def change_tag_counter(db: Session, tag_id: int, login: str, inc=True):
        if not TagManager.assert_tag_exists(db, tag_id, login):
            raise TagDoesNotExistException
        cur_usage = db.query(Tag).filter_by(id=tag_id, owner_id=login).one().usage_counter
        db.query(Tag).filter_by(id=tag_id, owner_id=login).update(
            {"usage_counter": cur_usage + 1 if inc else cur_usage - 1}
        )
        db.commit()

    @staticmethod
    def reset_tag_counter(db: Session, tag_id: int, login: str):
        if not TagManager.assert_tag_exists(db, tag_id, login):
            raise TagDoesNotExistException
        db.query(Tag).filter_by(id=tag_id, owner_id=login).update(
            {"usage_counter": 0}
        )
        db.commit()

    @staticmethod
    def delete_tag(db: Session, tag_id: int, login: str):
        if not TagManager.assert_tag_exists(db, tag_id, login):
            raise TagDoesNotExistException

        if not TagManager.assert_tag_is_not_used(db, tag_id, login):
            raise TagIsUsedException

        db.query(Tag).filter_by(id=tag_id, owner_id=login).delete()
        db.commit()
