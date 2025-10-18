from typing import Sequence, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from contextlib import contextmanager

from app.db.session_sql import get_db
from app.models_sql.product import Product
from app.schemas.product import ProductCreate, ProductOut

@contextmanager
def _session():
    gen = get_db()
    db: Session = next(gen)
    try:
        yield db
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

class SqlProductProvider:
    def list(self, skip: int = 0, limit: int = 50) -> List[ProductOut]:
        with _session() as db:
            stmt = (
                select(Product)
                .order_by(Product.Id)     # <-- key line
                .offset(skip)
                .limit(limit)
            )
            rows = db.execute(stmt).scalars().all()
            return [ProductOut.model_validate(r) for r in rows]

    def create(self, data: ProductCreate) -> ProductOut:
        with _session() as db:
            obj = Product(**data.model_dump())
            db.add(obj); db.commit(); db.refresh(obj)
            return ProductOut.model_validate(obj)
