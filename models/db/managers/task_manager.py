from sqlalchemy.orm import Session

from exceptions.custom_exceptions import PipelineDoesNotExistException, TaskListDoesNotExistException, \
    TaskDoesNotExistException, TagDoesNotExistException, TagIsAlreadyOnTask
from models.db.entities.tag import Tag
from models.db.entities.task import Task
from models.db.entities.task_list import TaskList
from models.db.managers.pipeline_manager import PipelineManager
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models.db.managers.tag_manager import TagManager


class TaskManager:
    @staticmethod
    def assert_task_list_exists(db: Session, board_id: int, task_list_id: int, login: str):
        return db.query(TaskList.id).filter_by(id=task_list_id, board_id=board_id, owner_id=login).scalar()

    @staticmethod
    def assert_task_exists(db: Session, board_id: int, task_list_id: int, task_id: int, login: str):
        return db.query(Task.id).filter_by(id=task_id, board_id=board_id, task_list_id=task_list_id,
                                           owner_id=login).scalar()

    @staticmethod
    def assert_pipelines_is_used_once(db: Session, board_id: int, username: str):
        pipelines_ids = set(
            map(lambda x: x.pipeline_id, db.query(Task).filter_by(board_id=board_id, owner_id=username).all()))
        for pipeline_id in pipelines_ids:
            if db.query(Task).filter(
                    (Task.board_id != board_id) &
                    (Task.pipeline_id == pipeline_id) &
                    (Task.owner_id == username)).scalar():
                return False
        return pipelines_ids

    @staticmethod
    def get_all_task_lists_for_user(db: Session, board_id: int, username: str):
        task_lists_ids = db.query(TaskList.id, TaskList.task_list_name) \
            .filter_by(owner_id=username, board_id=board_id) \
            .all()
        task_list_to_tasks = {}
        for (list_id, task_list_name) in task_lists_ids:
            tasks = db.query(Task).filter(Task.task_list_id == list_id).all()
            task_list_to_tasks[TaskList(id=list_id, task_list_name=task_list_name)] = tasks
        return task_list_to_tasks

    @staticmethod
    def add_task_list(db: Session, board_id: int, task_list_name: str, login: str):
        db.add(TaskList(task_list_name=task_list_name, board_id=board_id, owner_id=login, tags=set()))
        db.commit()

    @staticmethod
    def delete_task_list(db: Session, board_id: int, list_id: int, login: str):
        db.query(TaskList).filter_by(id=list_id, board_id=board_id, owner_id=login).delete()
        tasks = db.query(Task).filter_by(board_id=board_id, task_list_id=list_id, owner_id=login).all()
        for task in tasks:
            TaskManager.delete_task(db, board_id, list_id, task.id, login)
        db.commit()

    @staticmethod
    def add_task(db: Session, board_id: int, task_list_id: int, task_name: str, task_desc: str, is_done: bool,
                 pipeline_id: int,
                 login: str):
        if TaskManager.assert_task_list_exists(db, board_id, task_list_id, login):
            if PipelineManager.assert_owner_pipeline(db, pipeline_id, login):
                db.add(Task(
                    task_list_id=task_list_id,
                    board_id=board_id,
                    owner_id=login,
                    task_name=task_name,
                    task_desc=task_desc,
                    is_done=is_done,
                    pipeline_id=pipeline_id,
                    cur_pipeline_index=0,
                    tags=set()
                ))
                db.commit()
            else:
                raise PipelineDoesNotExistException
        else:
            raise TaskListDoesNotExistException

    @staticmethod
    def delete_task(db: Session, board_id: int, task_list_id: int, task_id: int, login: str):
        if TaskManager.assert_task_exists(db, board_id, task_list_id, task_id, login):
            task = db.query(Task).filter_by(id=task_id, owner_id=login).one()
            for tag in task.tags:
                TagManager.change_tag_counter(db, tag, login, inc=False)
            db.query(Task).filter_by(id=task_id, owner_id=login).delete()
            db.commit()
        else:
            raise TaskDoesNotExistException

    @staticmethod
    def change_status(db: Session, board_id: int, task_list_id: int, task_id: int, login: str):
        if TaskManager.assert_task_exists(db, board_id, task_list_id, task_id, login):
            task = db \
                .query(Task).filter_by(id=task_id, board_id=board_id, task_list_id=task_list_id, owner_id=login) \
                .one()
            cur_pipeline = PipelineManager.get_pipeline_by_id(db, task.pipeline_id, login)
            cur_index = task.cur_pipeline_index
            db.query(Task).filter_by(id=task_id, board_id=board_id, task_list_id=task_list_id, owner_id=login).update(
                {"is_done": cur_index + 2 >= len(cur_pipeline.pipeline),
                 "cur_pipeline_index": cur_index if cur_index + 1 >= len(cur_pipeline.pipeline) else cur_index + 1})
            db.commit()
        else:
            raise TaskDoesNotExistException

    @staticmethod
    def add_task_tag(db: Session, board_id: int, task_list_id: int, task_id: int, tag_id: int, login: str):
        if not TaskManager.assert_task_exists(db, board_id, task_list_id, task_id, login):
            raise TaskDoesNotExistException
        if not TagManager.assert_tag_exists(db, tag_id, login):
            raise TagDoesNotExistException
        tags = db \
            .query(Task).filter_by(id=task_id, board_id=board_id, task_list_id=task_list_id, owner_id=login) \
            .one().tags
        new_tag = db \
            .query(Tag).filter_by(id=tag_id, owner_id=login) \
            .one()
        if new_tag.id in tags:
            raise TagIsAlreadyOnTask
        tags.add(new_tag.id)
        TagManager.change_tag_counter(db, tag_id, login)
        db.query(Task).filter_by(id=task_id, board_id=board_id, task_list_id=task_list_id, owner_id=login).update(
            {"tags": tags})
        db.commit()

    @staticmethod
    def remove_task_tag(db: Session, board_id: int, task_list_id: int, task_id: int, tag_id: int, login: str):
        if not TaskManager.assert_task_exists(db, board_id, task_list_id, task_id, login):
            raise TaskDoesNotExistException
        if not TagManager.assert_tag_exists(db, tag_id, login):
            raise TagDoesNotExistException
        tags = db \
            .query(Task).filter_by(id=task_id, board_id=board_id, task_list_id=task_list_id, owner_id=login) \
            .one().tags
        tags = set(filter(lambda x: x != tag_id, tags))
        TagManager.change_tag_counter(db, tag_id, login, inc=False)
        db.query(Task).filter_by(id=task_id, board_id=board_id, task_list_id=task_list_id, owner_id=login).update(
            {"tags": tags})
        db.commit()
