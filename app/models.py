from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary, JSON, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
now = datetime.now()
# Post model


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=False, index=True)
    caption = Column(String)
    file_metadata = Column(JSON)
    date_posted = Column(String, default="not yet posted")
    date_added = Column(String, default=now.strftime("%Y/%m/%d, %H:%M:%S"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="owner")
