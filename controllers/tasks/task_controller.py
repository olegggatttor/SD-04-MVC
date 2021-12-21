from fastapi import APIRouter, Request, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from controllers.controllers_utils import get_db
from controllers.registration.login_controller import get_current_user_from_token
from exceptions.custom_exceptions import TaskListDoesNotExistException, PipelineDoesNotExistException, \
    TaskDoesNotExistException, TagDoesNotExistException, TagIsAlreadyOnTask
from models.db.database import Base, engine, SessionLocal
from models.db.managers.pipeline_manager import PipelineManager
from models.db.managers.tag_manager import TagManager
from models.db.managers.task_manager import TaskManager

api_router = APIRouter()

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="resources/templates/")


def redirect_to_main(board_id: int):
    return RedirectResponse('/tasks_lists/{}'.format(board_id), status_code=302)


@api_router.get("/tasks_lists/{board_id}")
def show_tasks_lists(board_id: int, request: Request, db: Session = Depends(get_db),
                     user=Depends(get_current_user_from_token)):
    tasks_lists = TaskManager.get_all_task_lists_for_user(db, board_id, user.login)
    pipelines = PipelineManager.get_all_pipelines_for_user(db, user.login)
    all_tags = TagManager.get_all_tags_for_user(db, user.login)
    return templates.TemplateResponse('form.html',
                                      {'request': request,
                                       'groups': tasks_lists,
                                       'board_id': board_id,
                                       'pipelines': dict(zip(map(lambda pipe: pipe.id, pipelines), pipelines)),
                                       'all_tags': dict(zip(map(lambda tag: tag.id, all_tags), all_tags))})


@api_router.post("/add_task_list/{board_id}", response_class=RedirectResponse)
def add_task_list(board_id: int, task_list_name: str = Form(...), db: Session = Depends(get_db),
                  user=Depends(get_current_user_from_token)):
    TaskManager.add_task_list(db, board_id, task_list_name, user.login)
    return redirect_to_main(board_id)


@api_router.post("/delete_task_list/{board_id}/{list_id}", response_class=RedirectResponse)
def delete_task_list(board_id: int, list_id: int, db: Session = Depends(get_db),
                     user=Depends(get_current_user_from_token)):
    TaskManager.delete_task_list(db, board_id, list_id, user.login)
    return redirect_to_main(board_id)


@api_router.post("/add_task/{board_id}/{task_list_id}", response_class=RedirectResponse)
def add_task(board_id: int, task_list_id: int, name: str = Form(...), desc: str = Form(...),
             is_done: bool = Form(False), pipeline_id=Form(...),
             db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    try:
        TaskManager.add_task(db, board_id, task_list_id, name, desc, is_done, pipeline_id, user.login)
    except TaskListDoesNotExistException:
        raise HTTPException(status_code=404, detail="No such task list for you.")
    except PipelineDoesNotExistException:
        raise HTTPException(status_code=404, detail="No such pipeline for you. try another one.")
    return redirect_to_main(board_id)


@api_router.post("/delete_task/{board_id}/{task_list_id}/{task_id}", response_class=RedirectResponse)
def delete_task(board_id: int, task_list_id: int, task_id: int, db: Session = Depends(get_db),
                user=Depends(get_current_user_from_token)):
    try:
        TaskManager.delete_task(db, board_id, task_list_id, task_id, user.login)
    except TaskDoesNotExistException:
        raise HTTPException(status_code=404, detail="No such task for you. try another one.")
    except TagDoesNotExistException:
        raise HTTPException(status_code=404, detail="Tag for task does not exist.")
    return redirect_to_main(board_id)


@api_router.post("/change_status/{board_id}/{task_list_id}/{task_id}", response_class=RedirectResponse)
def change_status(board_id: int, task_list_id: int, task_id: int, db: Session = Depends(get_db),
                  user=Depends(get_current_user_from_token)):
    try:
        TaskManager.change_status(db, board_id, task_list_id, task_id, user.login)
    except TaskDoesNotExistException:
        raise HTTPException(status_code=404, detail="No such task for you. try another one.")
    return redirect_to_main(board_id)


@api_router.post("/add_tag/{board_id}/{task_list_id}/{task_id}", response_class=RedirectResponse)
def add_tag(board_id: int, task_list_id: int, task_id: int, tag_id=Form(...), db: Session = Depends(get_db),
            user=Depends(get_current_user_from_token)):
    try:
        TaskManager.add_task_tag(db, board_id, task_list_id, task_id, tag_id, user.login)
    except TaskDoesNotExistException:
        raise HTTPException(status_code=404, detail="No such task for you. try another one.")
    except TagDoesNotExistException:
        raise HTTPException(status_code=404, detail="Tag for task does not exist.")
    except TagIsAlreadyOnTask:
        raise HTTPException(status_code=404, detail="You already have this tag on this task.")
    return redirect_to_main(board_id)


@api_router.post("/remove_tag/{board_id}/{task_list_id}/{task_id}/{tag_id}", response_class=RedirectResponse)
def remove_tag(board_id: int, task_list_id: int, task_id: int, tag_id: int, db: Session = Depends(get_db),
               user=Depends(get_current_user_from_token)):
    try:
        TaskManager.remove_task_tag(db, board_id, task_list_id, task_id, tag_id, user.login)
    except TaskDoesNotExistException:
        raise HTTPException(status_code=404, detail="No such task for you. try another one.")
    except TagDoesNotExistException:
        raise HTTPException(status_code=404, detail="Tag for task does not exist.")
    return redirect_to_main(board_id)
