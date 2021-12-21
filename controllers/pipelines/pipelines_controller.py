from fastapi import APIRouter, Request, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from controllers.controllers_utils import get_db
from controllers.registration.login_controller import get_current_user_from_token
from exceptions.custom_exceptions import PipelineDoesNotExistException, PipelineIsUsedException
from models.db.database import Base, engine
from models.db.managers.pipeline_manager import PipelineManager

pipelines_router = APIRouter()

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="resources/templates/")


def redirect_to_main():
    return RedirectResponse('/pipelines/', status_code=302)


@pipelines_router.get("/pipelines")
def get_pipelines_info(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    pipelines = PipelineManager.get_all_pipelines_for_user(db, user.login)
    return templates.TemplateResponse('pipelines.html', {'request': request, 'pipelines': pipelines})


@pipelines_router.post("/add_pipeline/", response_class=RedirectResponse)
def add_pipeline(pipeline_name=Form(...), db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    PipelineManager.add_pipeline(db, pipeline_name, user.login)
    return redirect_to_main()


@pipelines_router.post("/delete_pipeline/{pipeline_id}", response_class=RedirectResponse)
def delete_pipeline(pipeline_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    try:
        PipelineManager.delete_pipeline(db, pipeline_id, user.login)
    except PipelineDoesNotExistException:
        raise HTTPException(status_code=404, detail="Pipeline bot found.")
    except PipelineIsUsedException:
        raise HTTPException(status_code=404, detail="Remove pipeline from all tasks first.")
    return redirect_to_main()


@pipelines_router.post("/add_cell/{pipeline_id}", response_class=RedirectResponse)
def add_cell(pipeline_id: int, cell_name: str = Form(...), db: Session = Depends(get_db),
             user=Depends(get_current_user_from_token)):
    PipelineManager.add_cell(db, pipeline_id, cell_name, user.login)
    return redirect_to_main()


@pipelines_router.post("/delete_cell/{pipeline_id}/{cell_id}", response_class=RedirectResponse)
def delete_cell(pipeline_id: int, cell_id: int, db: Session = Depends(get_db),
                user=Depends(get_current_user_from_token)):
    try:
        PipelineManager.delete_cell(db, pipeline_id, cell_id, user.login)
    except PipelineDoesNotExistException:
        raise HTTPException(status_code=404, detail="Pipeline bot found.")
    except PipelineIsUsedException:
        raise HTTPException(status_code=404, detail="Remove pipeline from all tasks first.")
    return redirect_to_main()
