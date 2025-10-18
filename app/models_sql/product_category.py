from sqlalchemy import Column, Integer
from app.db.base import Base

class ProductCategory(Base):
    __tablename__ = "ProductCategory"  # CHANGE if needed
    id = Column(Integer, primary_key=True, index=True)
    ProductId = Column(Integer, nullable=False)
    CategoryId = Column(Integer, nullable=False)
