from sqlalchemy import Column, Integer, String
from app.db.base import Base

class SqlImage(Base):
    __tablename__ = "Image"  # CHANGE if needed
    Id = Column(Integer, primary_key=True, index=True)
    ProductId = Column(Integer, nullable=False)
    Extension = Column(String(10), nullable=False)
    
