from typing import List
from sqlalchemy import select, exists, and_,func, delete  
from sqlalchemy.orm import Session
from contextlib import contextmanager

from app.db.session_sql import get_db
from app.models_sql.product import SqlProduct
from app.models_sql.category import SqlCategory
from app.models_sql.product_category import SqlProductCategory
from app.models_sql.image import SqlImage
from app.models_sql.product_variation import SqlProductVariation
from app.models_sql.product_available_colours import SqlProductAvailableColours
from app.models_sql.orders import SqlOrderItem

from app.schemas.product import (
    GetProductRequest,
    ProductAvailableColoursModel,
    SaveProductRequest,
    ProductModel,
    ProductCategoryModel,
    CategoryModel,
    ProductImageModel,
    ProductVariationModel,
)
def _parse_image_ids_from_filenames(names: list[str]) -> set[int]:
    """
    Accept filenames like '123.jpg', '45.png', return {123, 45}.
    Ignores items that don't parse cleanly.
    """
    out: set[int] = set()
    for n in names or []:
        try:
            base = n.split('.')[0].strip()
            if base:
                out.add(int(base))
        except Exception:
            pass
    return out

def _attr(obj, *names):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return None

def _order_col(model, *names):
    for n in names:
        if hasattr(model, n):
            return getattr(model, n)
    return None
    

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


def _get_pagination(req: GetProductRequest) -> tuple[int, int]:
    """
    Support both PascalCase (Skip/Limit) and camelCase (skip/limit).
    Defaults: skip=0, limit=50.
    """
    skip = getattr(req, "Skip", None)
    if skip is None:
        skip = getattr(req, "skip", 0)

    limit = getattr(req, "Limit", None)
    if limit is None:
        limit = getattr(req, "limit", 50)

    # ensure ints and sane bounds
    try:
        skip = int(skip)
    except Exception:
        skip = 0
    try:
        limit = int(limit)
    except Exception:
        limit = 50
    if skip < 0:
        skip = 0
    if limit < 1:
        limit = 1
    if limit > 500:
        limit = 500
    return skip, limit


class ProductsRepository:
    # --- Products ---
    def get_products(self, req: GetProductRequest) -> List[ProductModel]:
        with _session() as db:
            # Base select
            stmt = select(SqlProduct)

            # Collect WHERE conditions (ANDed)
            conditions = []

            # Filter by Id (exact)
            if req.Id is not None and int(req.Id) > 0:
                conditions.append(  SqlProduct.Id == int(req.Id))

            # Filter by Name (contains, case-insensitive)
            if req.Name:
                name = req.Name.strip()
                if name:
                    conditions.append(
                        func.lower(SqlProduct.Name).like(f"%{name.lower()}%")
                    )

            # Filter by Description (contains)
            if req.Description:
                desc = req.Description.strip()
                if desc:
                    # Only add if column exists on your table
                    if hasattr(SqlProduct, "Description"):
                        conditions.append(
                            func.lower(SqlProduct.Description).like(f"%{desc.lower()}%")
                        )

            # Filter by Barcode (contains) — only if your Product table has a Barcode column
            if req.Barcode:
                bc = req.Barcode.strip()
                if bc and hasattr(SqlProduct, "Barcode"):
                    conditions.append(
                        func.lower(getattr(SqlProduct, "Barcode")).like(f"%{bc.lower()}%")
                    )

            # Filter by CategoryId/SubCategoryId via ProductCategory relation
            # If SubCategoryId provided > 0, we prioritize it; else CategoryId
            cat_id = None
            if req.SubCategoryId is not None and int(req.SubCategoryId) > 0:
                cat_id = int(req.SubCategoryId)
            elif req.CategoryId is not None and int(req.CategoryId) > 0:
                cat_id = int(req.CategoryId)

            if cat_id:
                conditions.append(
                    exists().where(
                        and_(
                            SqlProductCategory.ProductId == SqlProduct.Id,
                            SqlProductCategory.CategoryId == cat_id,
                        )
                    )
                )

            # Apply WHERE if we have any conditions
            if conditions:
                stmt = stmt.where(and_(*conditions))

            # MSSQL pagination requires ORDER BY
            skip = int(getattr(req, "Skip", 0) or 0)
            limit = int(getattr(req, "Limit", 50) or 50)
            if skip < 0: skip = 0
            if limit <= 0: limit = 5000
            if limit > 5000: limit = 5000

            stmt = stmt.order_by(SqlProduct.Id).offset(skip).limit(limit)

            rows = db.execute(stmt).scalars().all()
            return [ProductModel.model_validate(r, from_attributes=True) for r in rows]
    def _update_product_categories(self, db: Session, product_id: int, category_ids: list[int]) -> None:
        category_ids = [int(c) for c in (category_ids or []) if int(c) > 0]
        # Load existing
        existing = db.execute(
            select(SqlProductCategory).where(SqlProductCategory.ProductId == product_id)
        ).scalars().all()
        existing_set = {(pc.ProductId, pc.CategoryId) for pc in existing}
        desired_set = {(product_id, cid) for cid in category_ids}

        to_add = desired_set - existing_set
        to_del = existing_set - desired_set

        if to_add:
            db.add_all([SqlProductCategory(ProductId=pid, CategoryId=cid) for (pid, cid) in to_add])

        if to_del:
            db.execute(
                delete(SqlProductCategory).where(
                    (SqlProductCategory.ProductId == product_id) &
                    (SqlProductCategory.CategoryId.in_([cid for (_, cid) in to_del]))
                )
            )

    def _update_product_available_colours(self, db: Session, product_id: int, codes: list[str]) -> None:
        codes = [c.strip() for c in (codes or []) if c and c.strip()]
        existing = db.execute(
            select(SqlProductAvailableColours).where(SqlProductAvailableColours.ProductId == product_id)
        ).scalars().all()
        existing_codes = {e.Code for e in existing}
        desired_codes = set(codes)

        to_add = desired_codes - existing_codes
        to_del = existing_codes - desired_codes

        if to_add:
            db.add_all([SqlProductAvailableColours(ProductId=product_id, Code=code) for code in to_add])

        if to_del:
            db.execute(
                delete(SqlProductAvailableColours).where(
                    (SqlProductAvailableColours.ProductId == product_id) &
                    (SqlProductAvailableColours.Code.in_(list(to_del)))
                )
            )

    def _update_product_variations(self, db: Session, product_id: int, variations: list) -> None:
        """
        Upsert by Id when provided; insert when Id is None.
        Delete db variations that are not present in the incoming list (by Id).
        """
        incoming = variations or []
        incoming_by_id = {v.Id: v for v in incoming if getattr(v, "Id", None)}
        incoming_new = [v for v in incoming if not getattr(v, "Id", None)]

        # Load existing for this product
        existing = db.execute(
            select(SqlProductVariation).where(SqlProductVariation.ProductId == product_id)
        ).scalars().all()
        existing_ids = {ev.Id for ev in existing}

        # Updates
        for ev in existing:
            v = incoming_by_id.get(ev.Id)
            if v:
                if v.Price is not None:
                    ev.Price = v.Price
                ev.Description = v.Description or None

        # Inserts
        for v in incoming_new:
            db.add(SqlProductVariation(
                ProductId=product_id,
                Price=v.Price,
                Description=(v.Description or None)
            ))

        # Deletes: any existing Id not present in incoming IDs
        incoming_ids = {vid for vid in incoming_by_id.keys() if vid}
        to_delete = existing_ids - incoming_ids
        if to_delete:
            db.execute(
                delete(SqlProductVariation).where(
                    (SqlProductVariation.ProductId == product_id) &
                    (SqlProductVariation.Id.in_(list(to_delete)))
                )
            )

    def _update_product_images(self, db: Session, product_id: int, images: list[str], uploaded_images: list[str]) -> None:
        """
        C# logic: parse IDs from filenames in Images and UploadedImages,
        then delete images for this product whose Id is NOT in that set.
        """
        keep_ids = _parse_image_ids_from_filenames(images) | _parse_image_ids_from_filenames(uploaded_images)

        # IMPORTANT: Your C# had a likely bug: it filtered `im.Id == productId`!
        # Correct behavior is: delete rows where ProductId == productId AND Id NOT IN keep_ids
        if keep_ids:
            db.execute(
                delete(SqlImage).where(
                    (SqlImage.ProductId == product_id) &
                    (~SqlImage.Id.in_(list(keep_ids)))
                )
            )
        else:
            # If no lists provided, do nothing (preserve current images)
            pass    
    def save_product(self, req: SaveProductRequest) -> int:
        """
        Insert if Id is None/0; Update if Id > 0.
        Then sync Categories, AvailableColours, Variations, Images.
        """
        with _session() as db:
            with db.begin():  # atomic transaction
                pid = int(req.Id) if req.Id else 0

                if pid > 0:
                    obj = db.get(SqlProduct, pid)
                    if not obj:
                        return 0
                    # update fields
                    if req.Name is not None: obj.Name = req.Name
                    obj.Price = req.Price
                    obj.SalePrice = req.SalePrice
                    obj.Barcode = req.Barcode
                    obj.Description = req.Description or ""
                    obj.StockQuantity = req.StockQuantity or 0
                    db.flush()
                    product_id = obj.Id
                else:
                    obj = SqlProduct(
                        Name=req.Name,
                        Price=req.Price,
                        SalePrice=req.SalePrice,
                        Barcode=req.Barcode,
                        Description=req.Description or "",
                        StockQuantity=req.StockQuantity or 0,
                    )
                    db.add(obj)
                    db.flush()   # get Id without committing
                    product_id = obj.Id

                # --- related updates (mirror your C# calls) ---
                self._update_product_categories(db, product_id, req.Categories or [])
                self._update_product_available_colours(db, product_id, req.AvailableColours or [])
                self._update_product_variations(db, product_id, req.ProductVariations or [])
                self._update_product_images(db, product_id, req.Images or [], req.UploadedImages or [])

                # (optional) cache refresh stub
                # self._update_products_cache(obj)

            # transaction committed
            return int(product_id)

    def delete_product(self, product_id: int) -> bool:
         with _session() as db:
            # Exists?
            p = db.get(SqlProduct, product_id)
            if not p:
                return False

            # Referenced by orders? -> block with 409 at router
            refs = db.execute(
                select(func.count())
                .select_from(SqlOrderItem)
                .where(SqlOrderItem.ProductId == product_id)
            ).scalar_one()
            if refs and int(refs) > 0:
                return "referenced"

            # Delete children first (respect FKs), then parent; single commit
            try:
                db.execute(delete(SqlImage).where(SqlImage.ProductId == product_id))
                db.execute(delete(SqlProductVariation).where(SqlProductVariation.ProductId == product_id))
                db.execute(delete(SqlProductAvailableColours).where(SqlProductAvailableColours.ProductId == product_id))
                db.execute(delete(SqlProductCategory).where(SqlProductCategory.ProductId == product_id))

                db.delete(p)
                db.commit()
                return True
            except Exception:
                db.rollback()
                raise
   
    # --- ProductCategories ---    
    def get_product_categories(self) -> List[ProductCategoryModel]:
        with _session() as db:
        # tolerate Id vs id on the SQLAlchemy model
            order_col = _order_col(SqlProductCategory, "Id", "id")
            stmt = select(SqlProductCategory)
            if order_col is not None:
                stmt = stmt.order_by(order_col)

            rows = db.execute(stmt).scalars().all()

            # Build DTOs explicitly so casing mismatches don't break validation
            result: List[ProductCategoryModel] = []
            for r in rows:
                result.append(
                    ProductCategoryModel(
                        Id=_attr(r, "Id", "id"),
                        ProductId=_attr(r, "ProductId", "productId", "ProductID"),
                        CategoryId=_attr(r, "CategoryId", "categoryId", "CategoryID"),
                    )
                )
        return result


    # --- Categories ---
    def get_categories(self) -> List[CategoryModel]:
        with _session() as db:
            rows = db.execute(select(SqlCategory).order_by(SqlCategory.Id)).scalars().all()
            return [CategoryModel.model_validate(r, from_attributes=True) for r in rows]

    # --- Images ---
    def get_images(self) -> List[ProductImageModel]:
        with _session() as db:
            rows = db.execute(select(SqlImage).order_by(SqlImage.Id)).scalars().all()
            return [ProductImageModel.model_validate(r, from_attributes=True) for r in rows]

    # --- Product Variations ---
    def get_product_variations(self) -> List[ProductVariationModel]:
        with _session() as db:
            rows = db.execute(
                select(SqlProductVariation).order_by(SqlProductVariation.Id)
            ).scalars().all()
            return [
                ProductVariationModel.model_validate(r, from_attributes=True)
                for r in rows
            ]

    # --- Available Colours ---
    def get_available_colours(self) -> List[ProductAvailableColoursModel]:
        with _session() as db:
            rows = db.execute(
                select(SqlProductAvailableColours).order_by(SqlProductAvailableColours.Id)
            ).scalars().all()
            return [
                ProductAvailableColoursModel.model_validate(r, from_attributes=True)
                for r in rows
            ]
