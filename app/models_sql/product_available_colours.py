from sqlalchemy import Column, Integer, String
from app.db.base import Base
class SqlProductAvailableColours(Base):
    __tablename__ = "ProductAvailableColours"  # CHANGE if needed
    Id = Column(Integer, primary_key=True, index=True)
    ProductId = Column(Integer, nullable=False)
    Code = Column(String(20), nullable=False)
    
# SELECT TOP (1000) [Id]
#       ,[ProductId]
#       ,[Code]
#   FROM [Market].[dbo].[ProductAvailableColours]