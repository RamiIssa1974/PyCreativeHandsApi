# app/models_sql/purchase_image.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class SqlPurchaseImage(Base):
    __tablename__ = "PurchaseImage"
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    PurchaseId = Column(Integer, ForeignKey("Purchase.Id"), nullable=False)
    Extension = Column(String(50), nullable=False)  # store WITHOUT the dot, e.g. "jpg"
