from sqlalchemy.orm import Session
from sqlalchemy import update
from passlib.context import CryptContext
from . import models, schemas, ai, file_metadata
from fastapi import UploadFile, HTTPException, status, Request
import shutil
import os
import aiofiles


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_pwd = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()


def create_user_post(db: Session, item: schemas.PostCreate, user_id: int, add_caption: bool):
    db_item = models.Post(**item.model_dump(), owner_id=user_id)
    db_item.file_metadata = file_metadata.get_image_metadata(
        image=db_item.name, user_id=user_id)
    if add_caption:
        db_item.caption = ai.get_ig_caption(
            image=db_item.name, user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def add_post_caption(db: Session, items: list[schemas.PostBase], user_id: int):
    items_updated = []
    for item in items:
        row_to_update = db.query(models.Post).filter(
            models.Post.name == item.name).first()
        row_to_update.caption = ai.get_ig_caption(
            image=item.name, user_id=user_id)
        db.commit()
        updated_row = schemas.PostGet(name=row_to_update.name, date_added=row_to_update.date_added,
                                      date_posted=row_to_update.date_posted, caption=row_to_update.caption)
        items_updated.append(updated_row)
    return items_updated
