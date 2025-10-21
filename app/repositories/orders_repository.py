# app/repositories/orders_repository.py
from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.models_sql.orders import SqlOrder, SqlOrderItem, SqlOrderItemColour, SqlCustomer
from app.schemas.orders import (
    OrderModel, OrderItemModel, CustomerModel, ProductModel, ProductVariationModel,
    GetOrderRequest, AddToCartRequest, SaveOrderItemRequest,
    ChangeOrderStatusRequest, SendOrderRequest, MigrateAnonymousCartToUserRequest
)

class OrderStatusId:
    Cart = 1
    Accepted = 2
    Prepared = 3
    Sent = 4
    Paid = 5
    Canceled = 6
    Closed = 7

class OrdersRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------ helpers: loaders & mappers (no relationships) ------------

    def _load_customer(self, customer_id: int) -> Optional[SqlCustomer]:
        if not customer_id:
            return None
        return self.db.execute(
            select(SqlCustomer).where(SqlCustomer.Id == customer_id)
        ).scalar_one_or_none()

    def _load_items(self, order_id: int) -> List[SqlOrderItem]:
        return self.db.execute(
            select(SqlOrderItem).where(SqlOrderItem.OrderId == order_id)
        ).scalars().all()

    def _load_item_colours(self, order_item_id: int) -> List[SqlOrderItemColour]:
        return self.db.execute(
            select(SqlOrderItemColour).where(SqlOrderItemColour.OrderItemId == order_item_id)
        ).scalars().all()

    def _map_customer(self, c: Optional[SqlCustomer]) -> Optional[CustomerModel]:
        if c is None:
            return None
        return CustomerModel(
            id=c.Id,
            name=c.Name,
            tel1=c.Tel1,
            tel2=c.Tel2,
            address=c.Address,
            user=None,  # not projected
            notes=c.Notes,
            email=c.Email,
        )

    def _map_order_item(self, oi: SqlOrderItem) -> OrderItemModel:
        colours_rows = self._load_item_colours(oi.Id)
        colours = [r.Code for r in colours_rows] if colours_rows else None
        return OrderItemModel(
            id=oi.Id,
            order_id=oi.OrderId,
            unit_price=float(oi.UnitPrice),
            quantity=float(oi.Quantity),
            note=oi.Note,
            product_variation=ProductVariationModel(id=oi.ProductVariationId) if oi.ProductVariationId else None,
            product=ProductModel(id=oi.ProductId),
            colours=colours,
        )

    def _map_order(self, o: SqlOrder, include_items: bool = True) -> OrderModel:
        customer_row = self._load_customer(o.CustomerId)
        items: List[OrderItemModel] = []
        if include_items:
            for oi in self._load_items(o.Id):
                items.append(self._map_order_item(oi))
        return OrderModel(
            id=o.Id,
            user_id=o.UserId,
            customer_id=o.CustomerId,
            status_id=o.StatusId,
            delevery_price=float(o.DeleveryPrice or 0),
            create_date=o.CreateDate,
            address=o.Address,
            notes=o.Notes,
            discount=float(o.Discount or 0),
            customer=self._map_customer(customer_row),
            order_items=items,
        )

    def _upsert_order_item_colours(self, order_item_id: int, colours: Optional[List[str]]) -> None:
        if colours is None:
            return
        existing_rows = self._load_item_colours(order_item_id)
        existing = {r.Code for r in existing_rows}
        incoming = set(colours)

        # add new
        for code in incoming - existing:
            self.db.add(SqlOrderItemColour(OrderItemId=order_item_id, Code=code))

        # remove missing (only for this item)
        to_remove = [r for r in existing_rows if r.Code not in incoming]
        for r in to_remove:
            self.db.delete(r)

        self.db.flush()

    # ---------------------- C# parity methods ----------------------

    def get_order_by_id(self, order_id: int) -> Optional[OrderModel]:
        row = self.db.execute(
            select(SqlOrder).where(SqlOrder.Id == order_id)
        ).scalar_one_or_none()
        return self._map_order(row) if row else None

    def get_cart(self, user_id: str) -> Optional[OrderModel]:
        row = self.db.execute(
            select(SqlOrder).where(
                and_(SqlOrder.UserId == user_id, SqlOrder.StatusId == OrderStatusId.Cart)
            )
        ).scalar_one_or_none()
        return self._map_order(row) if row else None

    def get_empty_cart(self, user_id: str) -> OrderModel:
        return OrderModel(
            id=0,
            user_id=user_id,
            customer_id=0,
            status_id=OrderStatusId.Cart,
            delevery_price=0,
            create_date=datetime.now(),
            address="",
            notes=None,
            discount=0,
            customer=None,
            order_items=[],
        )

    def change_order_status(self, order: OrderModel) -> int:
        db_order = self.db.execute(
            select(SqlOrder).where(SqlOrder.Id == order.id)
        ).scalar_one_or_none()
        if not db_order:
            return -1
        db_order.StatusId = order.status_id
        self.db.flush()
        return db_order.Id

    def add_to_cart(self, req: AddToCartRequest) -> int:
        # find existing cart (by specific user or any when userId empty)
        cart = self.db.execute(
            select(SqlOrder).where(
                and_(
                    SqlOrder.StatusId == OrderStatusId.Cart,
                    or_(req.user_id is None, SqlOrder.UserId == req.user_id)
                )
            )
        ).scalar_one_or_none()

        def compute_unit_price() -> float:
            if req.product_unit_price and req.product_unit_price > 0:
                return float(req.product_unit_price)
            if req.product_sale_price and req.product_sale_price != 0 and req.product_sale_price < req.product_price:
                return float(req.product_sale_price)
            return float(req.product_price)

        if cart:
            # does a line with same product exist?
            exist_product = self.db.execute(
                select(SqlOrderItem).where(
                    and_(SqlOrderItem.OrderId == cart.Id, SqlOrderItem.ProductId == req.product_id)
                )
            ).scalar_one_or_none()

            if exist_product:
                if req.product_variation_id is None:
                    exist_product.Quantity = float(exist_product.Quantity) + float(req.quantity)
                    self.db.flush()
                    self._upsert_order_item_colours(exist_product.Id, req.order_item_colours)
                    return exist_product.Id
                else:
                    # try line with same variation
                    exist_variation = self.db.execute(
                        select(SqlOrderItem).where(
                            and_(SqlOrderItem.OrderId == cart.Id,
                                 SqlOrderItem.ProductVariationId == req.product_variation_id)
                        )
                    ).scalar_one_or_none()
                    if exist_variation:
                        exist_variation.Quantity = float(exist_variation.Quantity) + float(req.quantity)
                        self.db.flush()
                        self._upsert_order_item_colours(exist_variation.Id, req.order_item_colours)
                        return exist_variation.Id
                    else:
                        new_item = SqlOrderItem(
                            OrderId=cart.Id,
                            ProductId=req.product_id,
                            ProductVariationId=req.product_variation_id,
                            Quantity=req.quantity,
                            UnitPrice=compute_unit_price(),
                            Note=req.note or None
                        )
                        self.db.add(new_item)
                        self.db.flush()
                        self._upsert_order_item_colours(new_item.Id, req.order_item_colours)
                        return new_item.Id
            else:
                new_item = SqlOrderItem(
                    OrderId=cart.Id,
                    ProductId=req.product_id,
                    ProductVariationId=req.product_variation_id,
                    Quantity=req.quantity,
                    UnitPrice=compute_unit_price(),
                    Note=req.note or None
                )
                self.db.add(new_item)
                self.db.flush()
                self._upsert_order_item_colours(new_item.Id, req.order_item_colours)
                return new_item.Id
        else:
            # create cart
            global_customer_id = 1
            new_cart = SqlOrder(
                UserId=req.user_id,
                StatusId=OrderStatusId.Cart,
                CustomerId=global_customer_id,
                Discount=0,
                CreateDate=datetime.now(),
                DeleveryPrice=0
            )
            self.db.add(new_cart)
            self.db.flush()

            new_item = SqlOrderItem(
                OrderId=new_cart.Id,
                ProductId=req.product_id,
                Quantity=req.quantity,
                UnitPrice=compute_unit_price(),
                Note=req.note or None
            )
            self.db.add(new_item)
            self.db.flush()
            self._upsert_order_item_colours(new_item.Id, req.order_item_colours)
            return new_item.Id

    def send_order(self, req: SendOrderRequest) -> bool:
        o = self.db.execute(
            select(SqlOrder).where(
                and_(
                    SqlOrder.StatusId == OrderStatusId.Cart,
                    or_(SqlOrder.Id == req.order_id, SqlOrder.UserId == req.user_id)
                )
            )
        ).scalar_one_or_none()
        if not o:
            return False

        order_customer = self.db.execute(
            select(SqlCustomer).where(SqlCustomer.Id == o.CustomerId)
        ).scalar_one_or_none()

        global_user_id = 1
        if order_customer and o.CustomerId != global_user_id:
            order_customer.Name = req.customer_name
            order_customer.Tel1 = req.customer_tel
            order_customer.Notes = req.notes
            order_customer.Address = req.address
        else:
            order_customer = SqlCustomer(
                Name=req.customer_name,
                Tel1=req.customer_tel,
                Notes=req.notes,
                Address=req.address
            )
            self.db.add(order_customer)
            self.db.flush()

        o.CustomerId = order_customer.Id
        o.StatusId = OrderStatusId.Accepted
        o.UserId = None
        if req.notes:
            o.Notes = req.notes

        self.db.flush()
        # hook mailer here if needed
        return True

    def save_order(self, save_order: OrderModel) -> int:
        db_order = self.db.execute(
            select(SqlOrder).where(SqlOrder.Id == save_order.id)
        ).scalar_one_or_none()

        new_items_ids: List[int] = []

        if db_order:
            # update existing order
            db_order.CreateDate = save_order.create_date
            db_order.StatusId = save_order.status_id
            db_order.Address = save_order.address
            db_order.Discount = save_order.discount
            db_order.DeleveryPrice = save_order.delevery_price
            db_order.Notes = save_order.notes

            # update customer
            if db_order.CustomerId and save_order.customer:
                oc = self.db.execute(
                    select(SqlCustomer).where(SqlCustomer.Id == db_order.CustomerId)
                ).scalar_one_or_none()
                if oc:
                    # mirrors your C# (even though changing PK is unusual)
                    oc.Id = save_order.customer.id
                    oc.Name = save_order.customer.name
                    oc.Tel1 = save_order.customer.tel1
                    oc.Tel2 = save_order.customer.tel2
                    oc.Address = save_order.customer.address
                    oc.Email = save_order.customer.email
                    oc.Notes = save_order.customer.notes

            # upsert items
            for soi in save_order.order_items:
                db_item = None
                if soi.id:
                    db_item = self.db.execute(
                        select(SqlOrderItem).where(SqlOrderItem.Id == soi.id)
                    ).scalar_one_or_none()

                if db_item and soi.quantity > 0:
                    db_item.Quantity = soi.quantity
                    db_item.UnitPrice = soi.unit_price
                    self._upsert_order_item_colours(soi.id, soi.colours)
                elif db_item and soi.quantity == 0:
                    # delete colours then item
                    self.db.query(SqlOrderItemColour).filter(
                        SqlOrderItemColour.OrderItemId == db_item.Id
                    ).delete(synchronize_session=False)
                    self.db.delete(db_item)
                else:
                    # new item
                    new_item = SqlOrderItem(
                        Quantity=soi.quantity,
                        UnitPrice=soi.unit_price,
                        OrderId=save_order.id,
                        ProductId=soi.product.id,
                        Note=soi.note or None
                    )
                    self.db.add(new_item)
                    self.db.flush()
                    new_items_ids.append(new_item.Id)
                    self._upsert_order_item_colours(new_item.Id, soi.colours)

            # delete items not present in payload (excluding newly created)
            existing_ids = self.db.execute(
                select(SqlOrderItem.Id).where(SqlOrderItem.OrderId == save_order.id)
            ).scalars().all()

            payload_ids = [it.id for it in save_order.order_items if it.id]
            ids_to_delete = [iid for iid in existing_ids if iid not in payload_ids and iid not in new_items_ids]

            if ids_to_delete:
                self.db.query(SqlOrderItemColour).filter(
                    SqlOrderItemColour.OrderItemId.in_(ids_to_delete)
                ).delete(synchronize_session=False)
                self.db.query(SqlOrderItem).filter(
                    SqlOrderItem.Id.in_(ids_to_delete)
                ).delete(synchronize_session=False)

            self.db.flush()
            return db_order.Id
        else:
            # create new order
            new_order = SqlOrder(
                UserId=save_order.user_id,
                CustomerId=save_order.customer_id,
                StatusId=save_order.status_id,
                DeleveryPrice=save_order.delevery_price,
                CreateDate=save_order.create_date or datetime.now(),
                Address=save_order.address,
                Notes=save_order.notes,
                Discount=save_order.discount,
            )
            self.db.add(new_order)
            self.db.flush()

            for soi in save_order.order_items:
                new_item = SqlOrderItem(
                    Quantity=soi.quantity,
                    UnitPrice=soi.unit_price,
                    OrderId=new_order.Id,
                    ProductId=soi.product.id,
                    Note=soi.note or None
                )
                self.db.add(new_item)
                self.db.flush()
                self._upsert_order_item_colours(new_item.Id, soi.colours)

            self.db.flush()
            return new_order.Id

    def save_order_item(self, soi: SaveOrderItemRequest) -> int:
        if soi.id and soi.id > 0:
            db_item = self.db.execute(
                select(SqlOrderItem).where(SqlOrderItem.Id == soi.id)
            ).scalar_one_or_none()
            if not db_item:
                return -1
            db_item.Quantity = soi.quantity
            db_item.UnitPrice = soi.unit_price
            self._upsert_order_item_colours(soi.id, soi.colours)
            self.db.flush()
            return soi.id
        else:
            # merge by (OrderId, ProductId)
            existing = self.db.execute(
                select(SqlOrderItem).where(
                    and_(SqlOrderItem.OrderId == soi.order_id, SqlOrderItem.ProductId == soi.product_id)
                )
            ).scalar_one_or_none()
            if existing:
                existing.Quantity = float(existing.Quantity) + float(soi.quantity)
                existing.UnitPrice = soi.unit_price
                self._upsert_order_item_colours(existing.Id, soi.colours)
                self.db.flush()
                return existing.Id
            else:
                new_item = SqlOrderItem(
                    OrderId=soi.order_id,
                    ProductId=soi.product_id,
                    Quantity=soi.quantity,
                    UnitPrice=soi.unit_price,
                    Note=soi.note or None
                )
                self.db.add(new_item)
                self.db.flush()
                self._upsert_order_item_colours(new_item.Id, soi.colours)
                return new_item.Id

    def get_orders(self, req: GetOrderRequest) -> List[OrderModel] | None:
        # try match customer by provided fields
        order_customer = None
        if req.customer_id or req.customer_name or req.customer_tel:
            order_customer = self.db.execute(
                select(SqlCustomer).where(
                    or_(
                        SqlCustomer.Id == (req.customer_id or 0),
                        SqlCustomer.Tel1 == req.customer_tel if req.customer_tel else False,
                        SqlCustomer.Tel2 == req.customer_tel if req.customer_tel else False,
                        SqlCustomer.Name == req.customer_name if req.customer_name else False,
                    )
                )
            ).scalar_one_or_none()

        rows = self.db.execute(
            select(SqlOrder).where(
                or_(
                    SqlOrder.Id == (req.order_id or -1),
                    SqlOrder.CustomerId == (req.customer_id or -1),
                    (SqlOrder.CustomerId == order_customer.Id) if order_customer else False,
                    SqlOrder.StatusId == (req.status_id or -1),
                )
            )
        ).scalars().all()

        if not rows:
            return None

        mapped = [self._map_order(o) for o in rows]
        mapped.sort(key=lambda x: x.id, reverse=True)
        return mapped

    def migrate_anonymous_cart_to_user(self, req: MigrateAnonymousCartToUserRequest) -> int:
        db_order = self.db.execute(
            select(SqlOrder).where(
                and_(
                    or_(SqlOrder.UserId == (req.cart_token or ""), SqlOrder.UserId == (req.user_id or "")),
                    SqlOrder.StatusId == OrderStatusId.Cart
                )
            )
        ).scalar_one_or_none()
        if db_order:
            db_order.UserId = req.user_id
            self.db.flush()
            return db_order.Id
        return -1

    def delete_order_item(self, id: int) -> bool:
        db_item = self.db.execute(
            select(SqlOrderItem).where(SqlOrderItem.Id == id)
        ).scalar_one_or_none()
        if not db_item:
            return False

        # delete colours then item
        self.db.query(SqlOrderItemColour).filter(
            SqlOrderItemColour.OrderItemId == id
        ).delete(synchronize_session=False)
        self.db.flush()

        self.db.delete(db_item)
        self.db.flush()
        return True
