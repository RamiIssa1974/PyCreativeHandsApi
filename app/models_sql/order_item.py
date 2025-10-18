from sqlalchemy import Column, Integer, Numeric, String, DateTime
from app.db.base import Base

class OrderItem(Base):
    __tablename__ = "OrderItem"  # dbo.OrderItem

    Id = Column(Integer, primary_key=True, index=True)
    OrderId = Column(Integer, nullable=False, index=True)
    ProductId = Column(Integer, nullable=False, index=True)
    UnitPrice = Column(Numeric(18, 2), nullable=False)
    Quantity = Column(Numeric(18, 2), nullable=False)
    Note = Column(String(500), nullable=True)
    ProductVariationId = Column(Integer, nullable=True)
    ColourId = Column(String(50), nullable=True)
    CreateDate = Column(DateTime, nullable=False)
