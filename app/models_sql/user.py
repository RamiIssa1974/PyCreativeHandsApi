from sqlalchemy import Column, Integer, String
from app.db.base import Base

class SqlUser(Base):
    __tablename__ = "User"
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    UserName = Column(String(100), nullable=False, index=True)
    Password = Column(String(200), nullable=False)
    FullName = Column(String(200), nullable=True)
    IsAdmin = Column(Integer, nullable=False, default=0)  # SQL Server bit => 0/1
