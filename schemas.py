from pydantic import BaseModel


class PostBase(BaseModel):
    name: str
    file: object
    caption: str
    file_metadata: dict
    date_added: str
    date_posted: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Post] = []

    class Config:
        orm_mode = True
