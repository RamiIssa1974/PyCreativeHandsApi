from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import List

from app.db.session_sql import get_db
from app.repositories.orders_repository import OrdersRepository
from app.schemas.orders import (
    OrderModel, GetOrderRequest, AddToCartRequest, SaveOrderItemRequest,
    ChangeOrderStatusRequest, SendOrderRequest, MigrateAnonymousCartToUserRequest
)

def conditional_authorize():
    return True  # plug your real auth

def get_repo(db: Session = Depends(get_db)) -> OrdersRepository:
    return OrdersRepository(db)

# Base router (no /api here)
base_router = APIRouter(tags=["Orders"])

@base_router.get("/cart", response_model=OrderModel)
async def get_cart(userId: str = Query(...), repo: OrdersRepository = Depends(get_repo)):
    cart = await run_in_threadpool(repo.get_cart, userId)
    if cart is None:
        cart = await run_in_threadpool(repo.get_empty_cart, userId)
    return cart

@base_router.post("/Order", response_model=OrderModel)
async def get_order(request: GetOrderRequest, repo: OrdersRepository = Depends(get_repo)):
    if request is None or request.order_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request.")
    order = await run_in_threadpool(repo.get_order_by_id, request.order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return order

@base_router.post("/Orders", response_model=List[OrderModel], dependencies=[Depends(conditional_authorize)])
async def get_orders(request: GetOrderRequest, repo: OrdersRepository = Depends(get_repo)):
    if request is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request.")
    orders = await run_in_threadpool(repo.get_orders, request)
    return orders or []

@base_router.post("/add-to-cart", response_model=int, dependencies=[Depends(conditional_authorize)])
async def add_to_cart(request: AddToCartRequest, repo: OrdersRepository = Depends(get_repo)):
    order_item_id = await run_in_threadpool(repo.add_to_cart, request)
    return order_item_id

@base_router.post("/SaveOrder", response_model=int, dependencies=[Depends(conditional_authorize)])
async def save_order(order: OrderModel, repo: OrdersRepository = Depends(get_repo)):
    if order is None or not order.order_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order data.")
    order_id = await run_in_threadpool(repo.save_order, order)
    if order_id <= 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save the order.")
    return order_id

@base_router.post("/SaveOrderItem", response_model=int)
async def save_order_item(order_item: SaveOrderItemRequest, repo: OrdersRepository = Depends(get_repo)):
    if order_item is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order item data.")
    order_item_id = await run_in_threadpool(repo.save_order_item, order_item)
    if order_item_id <= 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save the order item.")
    return order_item_id

@base_router.post("/ChangeOrderStatus", response_model=int, dependencies=[Depends(conditional_authorize)])
async def change_order_status(order: OrderModel, repo: OrdersRepository = Depends(get_repo)):
    if order is None or order.id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order data.")
    updated_id = await run_in_threadpool(repo.change_order_status, order)
    if updated_id <= 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to change the order status.")
    return updated_id

@base_router.post("/ChangeOrderStatusByChangeOrderStatusRequest", response_model=int, dependencies=[Depends(conditional_authorize)])
async def change_order_status_by_request(request: ChangeOrderStatusRequest, repo: OrdersRepository = Depends(get_repo)):
    if request is None or request.id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data")
    order = await run_in_threadpool(repo.get_order_by_id, request.id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.status_id = request.status_id
    updated_id = await run_in_threadpool(repo.change_order_status, order)
    return updated_id

@base_router.post("/SendOrder", response_model=bool)
async def send_order(request: SendOrderRequest, repo: OrdersRepository = Depends(get_repo)):
    if request is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request data.")
    result = await run_in_threadpool(repo.send_order, request)
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send the order.")
    return result

@base_router.post("/migrate-cart", response_model=int)
async def migrate_anonymous_cart_to_user(request: MigrateAnonymousCartToUserRequest, repo: OrdersRepository = Depends(get_repo)):
    if request is None or not request.cart_token or not request.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order data.")
    order_id = await run_in_threadpool(repo.migrate_anonymous_cart_to_user, request)
    if order_id <= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cart found to migrate")
    return order_id

@base_router.delete("/DeleteOrderItem/{id}", response_model=bool, dependencies=[Depends(conditional_authorize)])
async def delete_order_item(id: int, repo: OrdersRepository = Depends(get_repo)):
    ok = await run_in_threadpool(repo.delete_order_item, id)
    return ok

# Final exported router mounts BOTH lowercase and uppercase
router = APIRouter()
router.include_router(base_router, prefix="/orders", tags=["Orders"])
router.include_router(base_router, prefix="/Orders", tags=["Orders"])
