from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Category(Base):
    __tablename__ = "Category"  # CHANGE if needed
    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(200), nullable=False)
    
