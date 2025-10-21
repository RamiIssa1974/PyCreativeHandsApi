# app/routers/purchase.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

# Use the same get_db used by your Orders/Products routers
from app.db.session_sql import get_db  # <-- adjust path if your project exposes get_db elsewhere
from app.repositories.purchase_repository import PurchaseRepository
from app.schemas.purchases import (
    GetPurchaseRequest,
    PurchaseModelIn,
    ProviderModelIn,
)

router = APIRouter()
_repo = PurchaseRepository()


# POST /GetPurchases
@router.post("/GetPurchases")
async def get_purchases(request: GetPurchaseRequest = Body(...), db: Session = Depends(get_db)):
    if request is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request data.")

    purchases = await run_in_threadpool(_repo.get_purchases, db, request)

    if not purchases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No purchases found for the given request.")

    return purchases  # PascalCase via schema serialization aliases


# GET /purchases?purchaseId=123
@router.get("/purchases")
async def get_purchases_by_id(purchaseId: int = Query(..., alias="purchaseId"), db: Session = Depends(get_db)):
    if purchaseId <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid purchase ID.")

    purchase = await run_in_threadpool(_repo.get_purchases_by_id, db, purchaseId)

    if purchase is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No purchase found with ID {purchaseId}.")

    return purchase


# POST /purchase
@router.post("/purchase", status_code=status.HTTP_201_CREATED)
async def save_purchase(purchase: PurchaseModelIn, db: Session = Depends(get_db)):
    if purchase is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid purchase data.")

    purchase_id = await run_in_threadpool(_repo.save_purchase, db, purchase)

    if purchase_id <= 0:
        # Match .NET: 500 on failure
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while saving the purchase.")

    # .NET returns CreatedAtAction with the integer id as the body
    return purchase_id


# GET /GetProviders
@router.get("/GetProviders")
async def get_providers(db: Session = Depends(get_db)):
    providers = await run_in_threadpool(_repo.get_providers, db)

    if not providers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No providers found.")

    return providers


# GET /GetProviderById/{id}
@router.get("/GetProviderById/{id}")
async def get_provider_by_id(id: int, db: Session = Depends(get_db)):
    provider = await run_in_threadpool(_repo.get_provider_by_id, db, id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return provider


# POST /SaveProvider
@router.post("/SaveProvider", status_code=status.HTTP_201_CREATED)
async def save_provider(provider: ProviderModelIn, db: Session = Depends(get_db)):
    if provider is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider cannot be null.")

    provider_id = await run_in_threadpool(_repo.save_provider, db, provider)

    if provider_id <= 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while saving the provider.")

    # .NET returns CreatedAtAction with integer id in body
    return provider_id


# DELETE /DeleteProvider/{ProviderId}
@router.delete("/DeleteProvider/{ProviderId}")
async def delete_provider(ProviderId: int, db: Session = Depends(get_db)):
    res = await run_in_threadpool(_repo.delete_provider, db, ProviderId)
    if res:
        # .NET returns 200 OK with string message
        return f"Provider with ID {ProviderId} deleted."
    else:
        # .NET returns 400 when not found (not 404)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Provider with ID {ProviderId} not found.")
