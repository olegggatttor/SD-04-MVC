from fastapi import APIRouter, Request, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from controllers.controllers_utils import get_db
from controllers.registration.login_controller import get_current_user_from_token
from exceptions.custom_exceptions import BoardDoesNotExistException, UserDoesNotExistException, SameUserException, \
    PipelineIsUsedInOtherBoards
from models.db.database import Base, engine
from models.db.managers.board_manager import BoardManager

boards_router = APIRouter()

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="resources/templates/")


def redirect_to_main():
    return RedirectResponse('/boards/', status_code=302)


@boards_router.get("/boards")
def get_boards_info(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    boards = BoardManager.get_all_boards_for_user(db, user.login)
    return templates.TemplateResponse('boards.html', {'request': request, 'boards': boards})


@boards_router.post("/add_board/", response_class=RedirectResponse)
def add_board(board_name=Form(...), db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    BoardManager.add_board(db, board_name, user.login)
    return redirect_to_main()


@boards_router.post("/delete_board/{board_id}", response_class=RedirectResponse)
def delete_board(board_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    try:
        BoardManager.delete_board(db, board_id, user.login)
    except BoardDoesNotExistException:
        raise HTTPException(status_code=404, detail="Board does not exist.")
    return redirect_to_main()


@boards_router.post("/change_board_owner/{board_id}", response_class=RedirectResponse)
def change_board_owner(board_id: int, new_owner=Form(...), db: Session = Depends(get_db),
                       user=Depends(get_current_user_from_token)):
    try:
        BoardManager.change_owner(db, board_id, new_owner, user.login)
    except BoardDoesNotExistException:
        raise HTTPException(status_code=404, detail="Board with such owner does not exist.")
    except UserDoesNotExistException:
        raise HTTPException(status_code=404, detail="New user not found")
    except SameUserException:
        raise HTTPException(status_code=404, detail="You can not give your board to yourself.")
    except PipelineIsUsedInOtherBoards:
        raise HTTPException(status_code=404, detail="All pipelines from tasks move with board. Some pipeline is used "
                                                    "in other boards.")
    return redirect_to_main()
