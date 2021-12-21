from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from controllers import settings
from controllers.controllers_utils import get_db
from controllers.registration.auth.oauth import OAuth2PasswordBearerWithCookie
from controllers.registration.forms.login_form import LoginForm
from models.db.database import Base, engine, SessionLocal
from controllers.registration.verify import verify_login, verify_password
from models.db.managers.user_manager import UserManager
from fastapi import HTTPException
from utils.constants import MIN_LOGIN_LENGTH, MAX_LOGIN_LENGTH, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH
from jwt import PyJWTError

auth_router = APIRouter()

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory='resources/templates/')
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_current_user_from_token(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        print("username/email extracted is ", username)
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = UserManager.get_user_credentials(db, login=username)
    if user is None:
        raise credentials_exception
    return user


@auth_router.get('/')
def goto_register():
    return RedirectResponse('/register/', status_code=302)


def goto_boards():
    return RedirectResponse('/boards/', status_code=302)


@auth_router.get("/register/")
def register(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})


@auth_router.post("/register/")
def register(login: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if not verify_login(login):
        raise HTTPException(status_code=404, detail="Login must be in range of ({}, {})"
                            .format(MIN_LOGIN_LENGTH, MAX_LOGIN_LENGTH))
    if UserManager.user_exists(db, login):
        raise HTTPException(status_code=404, detail="User with such login already exists.")
    if not verify_password(password):
        raise HTTPException(status_code=404, detail="Password must be in range of ({}, {})"
                            .format(MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH))
    UserManager.add_new_user(db, login, password)
    return RedirectResponse('/login/', status_code=302)


@auth_router.get("/login/")
def login(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = UserManager.get_user_credentials(db, login=username)
    if not user:
        return False
    if user.password != password:
        return False
    return user


@auth_router.post("/token")
def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.login}
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/login/")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful :)")
            response = goto_boards()
            print(login_for_access_token(response=response, form_data=form, db=db))
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)
