from fastapi import APIRouter, Request, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from controllers.controllers_utils import get_db
from controllers.registration.login_controller import get_current_user_from_token
from exceptions.custom_exceptions import TagDoesNotExistException, TagIsUsedException
from models.db.database import Base, engine
from models.db.managers.tag_manager import TagManager

tags_router = APIRouter()

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="resources/templates/")


def redirect_to_main():
    return RedirectResponse('/tags/', status_code=302)


@tags_router.get("/tags")
def get_tags(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    tags = TagManager.get_all_tags_for_user(db, user.login)
    return templates.TemplateResponse('tags.html', {'request': request, 'tags': tags})


@tags_router.post("/add_tag/", response_class=RedirectResponse)
def add_tag(tag_name=Form(...), db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    TagManager.add_tag(db, tag_name, user.login)
    return redirect_to_main()


@tags_router.post("/delete_tag/{tag_id}", response_class=RedirectResponse)
def delete_tag(tag_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    try:
        TagManager.delete_tag(db, tag_id, user.login)
    except TagDoesNotExistException:
        raise HTTPException(status_code=404, detail="You do not have such tag.")
    except TagIsUsedException:
        raise HTTPException(status_code=404, detail="Remove tag from all tasks first")
    return redirect_to_main()
