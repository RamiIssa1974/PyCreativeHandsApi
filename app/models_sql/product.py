from sqlalchemy import Column, Integer, String, Numeric
from app.db.base import Base

class Product(Base):
    __tablename__ = "Product"  # change to your real table if different
    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(200), nullable=False)
    Description = Column(String(2000))
    Price = Column(Numeric(18, 2))
    SalePrice = Column(Numeric(18, 2))
    Barcode = Column(String(100))
    StockQuantity = Column(Integer, default=0)


