from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    name: str


class PostCreate(PostBase):
    caption: str
    file_metadata: dict


class Post(PostBase):
    id: int
    owner_id: int
    date_added: str
    date_posted: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    posts: list[Post] = []

    class Config:
        orm_mode = True
