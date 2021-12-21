from sqlalchemy.orm import Session

from exceptions.custom_exceptions import PipelineDoesNotExistException, PipelineIsUsedException
from models.db.entities.pipeline import Pipeline
from models.db.entities.task import Task


class PipelineManager:
    @staticmethod
    def assert_owner_pipeline(db: Session, pipeline_id: int, username: str):
        return db.query(Pipeline).filter_by(id=pipeline_id, owner_id=username).scalar()

    @staticmethod
    def assert_pipeline_is_not_used(db: Session, pipeline_id: int, username: str):
        return len(db.query(Task).filter_by(pipeline_id=pipeline_id, owner_id=username).all()) == 0

    @staticmethod
    def get_all_pipelines_for_user(db: Session, username: str):
        pipelines = db.query(Pipeline).filter_by(owner_id=username).all()
        return pipelines

    @staticmethod
    def get_pipeline_by_id(db: Session, pipeline_id: int, username: str):
        pipeline = db.query(Pipeline).filter_by(id=pipeline_id, owner_id=username).one()
        return pipeline

    @staticmethod
    def add_pipeline(db: Session, pipeline_name: str, login: str):
        db.add(Pipeline(pipeline_name=pipeline_name, owner_id=login, pipeline=[]))
        db.commit()

    @staticmethod
    def add_cell(db: Session, pipeline_id: int, cell_name: str, login: str):
        if PipelineManager.assert_owner_pipeline(db, pipeline_id, login):
            cur_pipeline = db.query(Pipeline).filter_by(id=pipeline_id, owner_id=login).one().pipeline
            cur_pipeline.append(cell_name)

            db.query(Pipeline).filter_by(id=pipeline_id, owner_id=login).update(
                {"pipeline": cur_pipeline})
            db.commit()
        else:
            raise Exception

    @staticmethod
    def delete_pipeline(db: Session, pipeline_id: int, login: str):
        if PipelineManager.assert_owner_pipeline(db, pipeline_id, login):
            if PipelineManager.assert_pipeline_is_not_used(db, pipeline_id, login):
                db.query(Pipeline).filter_by(id=pipeline_id, owner_id=login).delete()
                db.commit()
            else:
                raise PipelineIsUsedException
        else:
            raise PipelineDoesNotExistException

    @staticmethod
    def delete_cell(db: Session, pipeline_id: int, cell_id: int, login: str):
        if PipelineManager.assert_owner_pipeline(db, pipeline_id, login):
            if PipelineManager.assert_pipeline_is_not_used(db, pipeline_id, login):
                cur_pipeline = db.query(Pipeline).filter_by(id=pipeline_id, owner_id=login).one().pipeline
                cur_pipeline.pop(cell_id)

                db.query(Pipeline).filter_by(id=pipeline_id, owner_id=login).update(
                    {"pipeline": cur_pipeline})
                db.commit()
            else:
                raise PipelineIsUsedException
        else:
            raise PipelineDoesNotExistException
