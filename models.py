from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship

from database import Base

class Post(Base):
    __tablename__ = "captioned_posts"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=False, index=True)
    #file = Column(put in the thing to allow files to be uploaded)
    caption = Column(String)
    metadata = Column(JSON)
    date_posted = Column(DateTime)
    date_added = Column(DateTime)


