from sqlalchemy import Column, Integer, String, DateTime, Numeric
from app.db.base import Base

class SqlOrder(Base):
    __tablename__ = "Order"
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CustomerId = Column(Integer, nullable=False, index=True)
    StatusId = Column(Integer, nullable=False, index=True)
    DeleveryPrice = Column(Numeric(18, 2), nullable=False)
    CreateDate = Column(DateTime, nullable=False)
    Address = Column(String(250), nullable=True)
    Notes = Column(String(500), nullable=True)
    Discount = Column(Numeric(18, 2), nullable=False)
    UserId = Column(String(50), nullable=True, index=True)

class SqlOrderItem(Base):
    __tablename__ = "OrderItem"
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    OrderId = Column(Integer, nullable=False, index=True)
    ProductId = Column(Integer, nullable=False, index=True)
    UnitPrice = Column(Numeric(18, 2), nullable=False)
    Quantity = Column(Numeric(18, 2), nullable=False)
    Note = Column(String(500), nullable=True)
    ProductVariationId = Column(Integer, nullable=True)
    ColourId = Column(String(50), nullable=True)
    CreateDate = Column(DateTime, nullable=False)

class SqlOrderItemColour(Base):
    __tablename__ = "OrderItemColour"
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    OrderItemId = Column(Integer, nullable=False, index=True)
    Code = Column(String(50), nullable=False)

class SqlCustomer(Base):
    __tablename__ = "Customer"
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String(250), nullable=False)
    Tel1 = Column(String(50), nullable=False)
    Tel2 = Column(String(50), nullable=True)
    Address = Column(String(250), nullable=True)
    UserId = Column(Integer, nullable=True)
    Notes = Column(String(250), nullable=True)
    Email = Column(String(50), nullable=True)
