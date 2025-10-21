# app/models_sql/video.py
from sqlalchemy import Column, Integer, NVARCHAR, Text
from app.db.base import Base

class SqlVideo(Base):
    __tablename__ = "Video"

    Id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    Title = Column(NVARCHAR(50), nullable=True)
    Name = Column(NVARCHAR(50), nullable=False)
    Description = Column(Text, nullable=True)     # nvarchar(max)
    Extension = Column(NVARCHAR(5), nullable=False)
