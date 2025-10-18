from sqlalchemy import Column, Integer, String, Numeric
from app.db.base import Base

class ProductVariation(Base):
    __tablename__ = "ProductVariation"  # CHANGE if needed
    Id = Column(Integer, primary_key=True, index=True)
    ProductId = Column(Integer, nullable=False)
    Price = Column(Numeric(10, 2), nullable=False)
    Description = Column(String(500), nullable=True)
    
# SELECT TOP (1000) [Id]
#       ,[ProductId]
#       ,[Price]
#       ,[Description]
#   FROM [Market].[dbo].[ProductVariation]