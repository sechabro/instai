from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    name: str


class PostCreate(PostBase):
    id: int
    owner_id: int
    date_added: str
    date_posted: str
    caption: str
    file_metadata: dict

    class Config:
        from_attributes = True


class PostGet(PostBase):
    id: int
    date_added: str
    date_posted: str
    caption: str
    file_metadata: dict

    class Config:
        from_attributes: True


'''class PostCreate(PostBase):
    caption: str
    file_metadata: dict'''


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    posts: list[PostCreate] = []

    class Config:
        orm_mode = True


class UserOAuth(BaseModel):
    email: str | None = None
    is_active: bool | None = None


class UserInDB(UserOAuth):
    id: int
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
