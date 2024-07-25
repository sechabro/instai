from typing import Union, Annotated
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import schemas, crud, models, ai
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .oauth import *
from .schemas import UserOAuth
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()


http_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="You must be logged in to perform this action",
    headers={"WWW-Authenticate": "Bearer"}
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


'''@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user'''


@app.get("/posts/", response_model=list[schemas.PostGet])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
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
    current_user: Annotated[UserOAuth, Depends(get_current_active_user)],
):
    return current_user


@app.post("/users/me/add", response_model=schemas.PostGet)
async def add_post_for_user(current_user: Annotated[UserOAuth, Depends(read_current_user)], item: schemas.PostBase, db: Session = Depends(get_db)):
    user = current_user
    if not user:
        raise http_exception
    else:
        return crud.create_user_post(db=db, item=item, user_id=user.id)


@app.post("/users/me/uploadfiles", response_model=[])
async def create_upload_files(files: list[UploadFile], current_user: Annotated[UserOAuth, Depends(read_current_user)]):
    user = current_user
    if not user:
        raise http_exception
    else:
        return [{"filename": file.filename, "size": file.size} for file in files]
