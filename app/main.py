from typing import Union, Annotated
from fastapi import FastAPI, Request, Depends, HTTPException, status, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import schemas, crud, models, ai
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .oauth import *
from .schemas import UserOAuth, Token
import aiofiles
import os
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
current_user = Annotated[UserOAuth, Depends(get_current_active_user)]


def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()


db: Session = Depends(get_db)


ROOT_DIR = os.getcwd()
UP_DIR = os.path.join(ROOT_DIR, "uploads")
IMG_TYPE = ['image/jpeg', 'image/png']

http_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="You must be logged in to perform this action",
    headers={"WWW-Authenticate": "Bearer"}
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db=db):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db=db):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/posts", response_model=list[schemas.PostGet])
def read_items(skip: int = 0, limit: int = 100, db=db):
    items = crud.get_posts(db, skip=skip, limit=limit)
    return items


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


############ OAUTH REQUIRED ############
@app.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(
        db=SessionLocal, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me")
async def read_current_user(
    current_user: current_user,
):
    return current_user


@app.post("/users/me/upload", response_model=list[schemas.PostGet])
async def upload_files(files: list[UploadFile], current_user: current_user, add_caption: bool, db=db):
    user = current_user
    if not user:
        raise http_exception
    else:
        results = []
        for file in files:
            if file.content_type not in IMG_TYPE:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"{file.content_type} file type not permitted. Only PNG and Jpeg formats are permitted"
                )
            up_dir_user = f"{UP_DIR}/{str(user.id)}"
            if not os.path.isdir(up_dir_user):
                up_dir_user = os.path.join(UP_DIR, str(user.id))
                os.mkdir(up_dir_user)
            file_path = os.path.join(up_dir_user, file.filename)
            try:
                async with aiofiles.open(file_path, "wb") as new_file:
                    while file_content := await file.read(1024 * 1024):
                        await new_file.write(file_content)
            except Exception as e:
                return {"message": {e}}
            finally:
                await file.close()
                post = crud.create_user_post(db=db, item=schemas.PostBase(
                    name=file.filename), user_id=user.id, add_caption=add_caption)
                result = schemas.PostGet(
                    name=post.name, date_added=post.date_added, date_posted=post.date_posted, caption=post.caption, file_metadata=post.file_metadata)
                results.append(result)
        return results


@app.put("/users/me/caption", response_model=list[schemas.PostGet])
async def caption_file(files: list[schemas.PostBase], current_user: current_user, db=db):
    user = current_user
    if not user:
        raise http_exception
    else:
        return crud.add_post_caption(db=db, items=files, user_id=user.id)
