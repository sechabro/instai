from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary, JSON, TIMESTAMP
from sqlalchemy.orm import relationship

from database import Base

# Post model


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=False, index=True)
    file = Column(LargeBinary)
    caption = Column(String)
    file_metadata = Column(JSON)
    date_posted = Column(TIMESTAMP(timezone=True))
    date_added = Column(TIMESTAMP(timezone=True))
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="owner")
    # items = relationship("Item", back_populates="owner")


'''class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")'''
