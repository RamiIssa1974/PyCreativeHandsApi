# app/models_sql/purchases.py
from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Boolean, Text, NVARCHAR
from sqlalchemy.orm import relationship

# IMPORTANT: use the same Base as your existing models (Orders/Products).
# If your Base lives elsewhere, change this import to match (e.g., app.db.base).
from app.db.base import Base  # <-- adjust if your project uses a different Base path


class Provider(Base):
    __tablename__ = "Provider"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(NVARCHAR(500), nullable=False)
    IdN = Column(String(10), nullable=True)            # nchar(10) in SQL; stored as String(10)
    Address = Column(NVARCHAR(500), nullable=True)
    Tel1 = Column(NVARCHAR(50), nullable=True)
    Tel2 = Column(NVARCHAR(50), nullable=True)
    Email = Column(NVARCHAR(50), nullable=True)
    Description = Column(NVARCHAR(500), nullable=True)
    WebSite = Column(NVARCHAR(500), nullable=True)
    IsActive = Column(Boolean, nullable=False)


class Purchase(Base):
    __tablename__ = "Purchase"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    ProviderId = Column(Integer, ForeignKey("Provider.Id"), nullable=False)
    Date = Column(DateTime, nullable=False)
    Amount = Column(DECIMAL(18, 2), nullable=False)
    Description = Column(Text, nullable=True)          # nvarchar(max)
    PurchaseLink = Column(Text, nullable=True)         # nvarchar(max)

    # Minimal relationships only if needed (joins preferred in repository)
    # provider = relationship("Provider", lazy="joined")

 