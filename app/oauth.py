from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from . import crud
from .database import SessionLocal


def fake_hash_password(password: str):
    return password + "notreallyhashed"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    email: str | None = None
    is_active: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    user = crud.get_user_by_email(
        db=db, email=username)
    if user:
        user_dict = {
            "email": user.email,
            "hashed_password": user.hashed_password,
            "is_active": user.is_active
        }
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(SessionLocal, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # email = current_user.email
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
