from sqlalchemy.orm import Session

from exceptions.custom_exceptions import BoardDoesNotExistException, UserDoesNotExistException, SameUserException, \
    PipelineIsUsedInOtherBoards
from models.db.entities.board import Board
from models.db.entities.pipeline import Pipeline
from models.db.entities.task import Task
from models.db.entities.task_list import TaskList
from models.db.managers.tag_manager import TagManager
from models.db.managers.task_manager import TaskManager
from models.db.managers.user_manager import UserManager


class BoardManager:
    @staticmethod
    def assert_board_exists(db: Session, board_id: int, login: str):
        return db.query(Board).filter_by(id=board_id, owner_id=login).scalar()

    @staticmethod
    def get_all_boards_for_user(db: Session, username: str):
        boards = db.query(Board).filter_by(owner_id=username).all()
        return boards

    @staticmethod
    def add_board(db: Session, board_name: str, login: str):
        db.add(Board(board_name=board_name, owner_id=login))
        db.commit()

    @staticmethod
    def delete_board(db: Session, board_id: int, login: str):
        if BoardManager.assert_board_exists(db, board_id, login):
            db.query(Board).filter_by(id=board_id, owner_id=login).delete()
            task_lists = db.query(TaskList).filter_by(board_id=board_id, owner_id=login).all()
            for task_list in task_lists:
                TaskManager.delete_task_list(db, board_id, task_list.id, login)
            db.commit()
        else:
            raise BoardDoesNotExistException

    @staticmethod
    def change_owner(db: Session, board_id: int, new_owner: str, login: str):
        if not BoardManager.assert_board_exists(db, board_id, login):
            raise BoardDoesNotExistException
        if not UserManager.user_exists(db, new_owner):
            print('New user not exists.')
            raise UserDoesNotExistException
        if login == new_owner:
            print('Same user.')
            raise SameUserException
        maybe_pipelines = TaskManager.assert_pipelines_is_used_once(db, board_id, login)
        if not maybe_pipelines:
            raise PipelineIsUsedInOtherBoards
        all_tasks = db.query(Task).filter_by(board_id=board_id, owner_id=login).all()
        for task in all_tasks:
            for tag in task.tags:
                TagManager.change_tag_counter(db, tag, login, inc=False)
        db.query(Board).filter_by(id=board_id, owner_id=login).update(
            {"owner_id": new_owner}
        )
        db.query(TaskList).filter_by(board_id=board_id, owner_id=login).update(
            {"owner_id": new_owner}
        )
        db.query(Task).filter_by(board_id=board_id, owner_id=login).update(
            {"owner_id": new_owner, "tags": set()}
        )
        db.query(Pipeline).filter(Pipeline.id.in_(maybe_pipelines)).update(
            {"owner_id": new_owner}
        )
        db.commit()
