# app/schemas/orders.py

from typing import List, Optional, Annotated
from pydantic import BaseModel, ConfigDict, Field, AliasChoices
from datetime import datetime

# ---------- alias generators ----------
def to_camel(s: str) -> str:
    parts = s.split('_')
    return parts[0] + ''.join(w.capitalize() for w in parts[1:])

def to_pascal(s: str) -> str:
    return ''.join(w.capitalize() for w in s.split('_'))

# ---------- base models ----------
class CamelModel(BaseModel):
    """Use for request models if you want camelCase serialization (not critical for requests)."""
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

class PascalModel(BaseModel):
    """Use for response models so keys match legacy/.NET style (PascalCase)."""
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_pascal)

# ---------- dependent / nested response models ----------
# If you already have these in another module, you can import and delete these placeholders.
class ProductModel(PascalModel):
    id: int
    name: Optional[str] = None

class ProductVariationModel(PascalModel):
    id: int
    name: Optional[str] = None

class UserModel(PascalModel):
    id: Optional[str] = None
    user_name: Optional[str] = None

class CustomerModel(PascalModel):
    id: int
    name: str
    tel1: str
    tel2: Optional[str] = None
    address: Optional[str] = None
    user: Optional[UserModel] = None
    notes: Optional[str] = None
    email: Optional[str] = None

class OrderItemModel(PascalModel):
    id: int
    order_id: int
    unit_price: float
    quantity: float
    note: Optional[str] = None
    product_variation: Optional[ProductVariationModel] = None
    product: ProductModel
    colours: Optional[List[str]] = None

class OrderModel(PascalModel):
    id: int
    user_id: Optional[str] = None
    customer_id: int
    status_id: int
    delevery_price: float
    create_date: datetime
    address: Optional[str] = None
    notes: Optional[str] = None
    discount: float
    customer: Optional[CustomerModel] = None
    order_items: List[OrderItemModel]

# ---------- request models (accept both camelCase & PascalCase) ----------
class GetOrderRequest(CamelModel):
    order_id: Annotated[int, Field(validation_alias=AliasChoices("orderId", "OrderId"))] = 0
    customer_id: Annotated[int, Field(validation_alias=AliasChoices("customerId", "CustomerId"))] = 0
    customer_name: Annotated[str, Field(validation_alias=AliasChoices("customerName", "CustomerName"))] = ""
    customer_tel: Annotated[str, Field(validation_alias=AliasChoices("customerTel", "CustomerTel"))] = ""
    status_id: Annotated[int, Field(validation_alias=AliasChoices("statusId", "StatusId"))] = 0

class AddToCartRequest(CamelModel):
    user_id: Annotated[str, Field(validation_alias=AliasChoices("userId", "UserId"))]
    product_id: Annotated[int, Field(validation_alias=AliasChoices("productId", "ProductId"))]
    product_variation_id: Annotated[Optional[int], Field(default=None, validation_alias=AliasChoices("productVariationId", "ProductVariationId"))]
    quantity: Annotated[float, Field(validation_alias=AliasChoices("quantity", "Quantity"))]
    product_price: Annotated[float, Field(validation_alias=AliasChoices("productPrice", "ProductPrice"))]
    product_sale_price: Annotated[float, Field(validation_alias=AliasChoices("productSalePrice", "ProductSalePrice"))]
    product_unit_price: Annotated[float, Field(validation_alias=AliasChoices("productUnitPrice", "ProductUnitPrice"))]
    order_id: Annotated[int, Field(validation_alias=AliasChoices("orderId", "OrderId"))] = 0
    note: Annotated[str, Field(validation_alias=AliasChoices("note", "Note"))] = ""
    order_item_colours: Annotated[Optional[List[str]], Field(default=None, validation_alias=AliasChoices("orderItemColours", "OrderItemColours"))]

class SaveOrderItemRequest(CamelModel):
    id: Annotated[int, Field(validation_alias=AliasChoices("id", "Id"))] = 0
    order_id: Annotated[int, Field(validation_alias=AliasChoices("orderId", "OrderId"))]
    product_id: Annotated[int, Field(validation_alias=AliasChoices("productId", "ProductId"))]
    unit_price: Annotated[float, Field(validation_alias=AliasChoices("unitPrice", "UnitPrice"))]
    quantity: Annotated[float, Field(validation_alias=AliasChoices("quantity", "Quantity"))]
    note: Annotated[Optional[str], Field(default=None, validation_alias=AliasChoices("note", "Note"))]
    product_variation: Annotated[Optional[ProductVariationModel], Field(default=None, validation_alias=AliasChoices("productVariation", "ProductVariation"))]
    colours: Annotated[Optional[List[str]], Field(default=None, validation_alias=AliasChoices("colours", "Colours"))]

class ChangeOrderStatusRequest(CamelModel):
    id: Annotated[int, Field(validation_alias=AliasChoices("id", "Id"))]
    status_id: Annotated[int, Field(validation_alias=AliasChoices("statusId", "StatusId"))]

class SendOrderRequest(CamelModel):
    order_id: Annotated[int, Field(validation_alias=AliasChoices("orderId", "OrderId"))]
    user_id: Annotated[str, Field(validation_alias=AliasChoices("userId", "UserId"))]
    customer_name: Annotated[str, Field(validation_alias=AliasChoices("customerName", "CustomerName"))]
    customer_tel: Annotated[str, Field(validation_alias=AliasChoices("customerTel", "CustomerTel"))]
    address: Annotated[str, Field(validation_alias=AliasChoices("address", "Address"))]
    notes: Annotated[Optional[str], Field(default=None, validation_alias=AliasChoices("notes", "Notes"))]

class MigrateAnonymousCartToUserRequest(CamelModel):
    cart_token: Annotated[Optional[str], Field(default=None, validation_alias=AliasChoices("cartToken", "CartToken"))] = None
    user_id: Annotated[Optional[str], Field(default=None, validation_alias=AliasChoices("userId", "UserId"))] = None
