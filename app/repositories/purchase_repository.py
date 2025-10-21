# app/repositories/purchase_repository.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, Iterable, List

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models_sql.purchases import Provider, Purchase
from app.models_sql.purchase_image import SqlPurchaseImage
from app.schemas.purchases import (
    GetPurchaseRequest,
    PurchaseModelIn,
    PurchaseModel,
    ProviderModelIn,
    ProviderModel,
)


class PurchaseRepository:
    """
    Sync repository mirroring the C# logic and edge cases.
    Routers call these via run_in_threadpool.
    """

    # -------- Purchases --------

    def get_purchases_by_id(self, db: Session, purchase_id: int) -> Optional[PurchaseModel]:
        entity = db.query(Purchase).filter(Purchase.Id == purchase_id).first()
        if not entity:
            return None

        # Map to .NET-shaped model (CreateDate is string dd/MM/yyyy)
        return PurchaseModel(
            Id=entity.Id,
            ProviderId=entity.ProviderId,
            Amount=float(entity.Amount),
            CreateDate=entity.Date.strftime("%d/%m/%Y"),
            Description=entity.Description,
            PurchaseLink=entity.PurchaseLink,
            Image=None,  # not stored in Purchase; images go to PurchaseImage
        )

    def _parse_createdate(self, s: str) -> datetime:
        # .NET uses DateTime.TryParseExact("dd/MM/yyyy")
        return datetime.strptime(s, "%d/%m/%Y")

    def save_purchase(self, db: Session, purchase: PurchaseModelIn) -> int:
        """
        Returns new/existing Purchase Id on success; -1 on failure (to match C# repo).
        """
        try:
            # Parse CreateDate (string dd/MM/yyyy)
            purchase_create_date = self._parse_createdate(purchase.CreateDate)

            if purchase.Id:
                entity = db.query(Purchase).filter(Purchase.Id == purchase.Id).first()
            else:
                entity = None

            if entity:
                # Update existing
                entity.Date = purchase_create_date
                entity.Amount = purchase.Amount
                entity.Description = purchase.Description
                entity.ProviderId = purchase.ProviderId
                entity.PurchaseLink = purchase.PurchaseLink
                db.flush()
                purchase_id = entity.Id
            else:
                # Insert new
                entity = Purchase(
                    ProviderId=purchase.ProviderId,
                    Date=purchase_create_date,
                    Amount=purchase.Amount,
                    Description=purchase.Description,
                    PurchaseLink=purchase.PurchaseLink,
                )
                db.add(entity)
                db.flush()  # get identity Id
                purchase_id = entity.Id

                # If Image provided, create PurchaseImage row with Extension
                if purchase.Image:
                    # Split by '.', take the part after the first dot (same as C# Split('.')[1])
                    parts = purchase.Image.split(".")
                    if len(parts) > 1 and parts[1]:
                        ext = parts[1]
                        db.add(SqlPurchaseImage(PurchaseId=purchase_id, Extension=ext))

            db.commit()
            return purchase_id or -1
        except Exception:
            db.rollback()
            # C# logs and returns -1 instead of throwing
            return -1

    def get_purchases(self, db: Session, req: GetPurchaseRequest) -> Optional[List[PurchaseModel]]:
        """
        Returns list on success; None if empty (to let router return 404 like .NET).
        Date filtering uses the same minDate behavior as C#: if FromDate is null or <= 2000-01-01, ignore range.
        """
        min_date = datetime(2000, 1, 1)

        q = db.query(Purchase)

        if req.Id is not None and req.Id != -1:
            q = q.filter(Purchase.Id == req.Id)

        if req.ProviderId is not None and req.ProviderId != -1:
            q = q.filter(Purchase.ProviderId == req.ProviderId)

        # Apply date range only if FromDate is not null and > minDate (mirrors C# conditions)
        if req.FromDate and req.FromDate > min_date:
            q = q.filter(Purchase.Date >= req.FromDate)

        if req.ToDate and (not req.FromDate or req.FromDate <= min_date or req.ToDate >= min_date):
            # C# condition is asymmetric; keep it: second comparison uses rq.Date <= request.ToDate when FromDate check passes
            q = q.filter(Purchase.Date <= req.ToDate)

        entities = q.all()

        if not entities:
            return None

        result: List[PurchaseModel] = []
        for e in entities:
            result.append(
                PurchaseModel(
                    Id=e.Id,
                    ProviderId=e.ProviderId,
                    Amount=float(e.Amount),
                    CreateDate=e.Date.strftime("%d/%m/%Y"),
                    Description=e.Description,
                    PurchaseLink=e.PurchaseLink,
                    Image=None,
                )
            )
        return result

    # -------- Providers --------

    def save_provider(self, db: Session, provider: ProviderModelIn) -> int:
        try:
            entity = None
            if provider.Id:
                entity = db.query(Provider).filter(Provider.Id == provider.Id).first()

            if entity:
                # update
                entity.Name = provider.Name
                entity.IdN = provider.IdN
                entity.Description = provider.Description
                entity.Address = provider.Address
                entity.Tel1 = provider.Tel1
                entity.Tel2 = provider.Tel2
                entity.Email = provider.Email
                entity.WebSite = provider.WebSite
                entity.IsActive = provider.IsActive
            else:
                entity = Provider(
                    Name=provider.Name,
                    IdN=provider.IdN,
                    Description=provider.Description,
                    Address=provider.Address,
                    Tel1=provider.Tel1,
                    Tel2=provider.Tel2,
                    Email=provider.Email,
                    WebSite=provider.WebSite,
                    IsActive=provider.IsActive if provider.IsActive is not None else True,
                )
                db.add(entity)

            db.commit()
            return entity.Id
        except Exception:
            db.rollback()
            # C# returns -1 on failure
            return -1

    def get_providers(self, db: Session) -> Optional[List[ProviderModel]]:
        entities = db.query(Provider).all()
        if not entities:
            return None

        return [
            ProviderModel(
                Id=e.Id,
                Name=e.Name,
                IdN=e.IdN,
                Tel1=e.Tel1,
                Tel2=e.Tel2,
                Address=e.Address,
                Description=e.Description,
                WebSite=e.WebSite,
                Email=e.Email,
                IsActive=bool(e.IsActive),
            )
            for e in entities
        ]

    def get_provider_by_id(self, db: Session, provider_id: int) -> Optional[ProviderModel]:
        e = db.query(Provider).filter(Provider.Id == provider_id).first()
        if not e:
            return None

        return ProviderModel(
            Id=e.Id,
            Name=e.Name,
            IdN=e.IdN,
            Tel1=e.Tel1,
            Tel2=e.Tel2,
            Address=e.Address,
            Description=e.Description,
            WebSite=e.WebSite,
            Email=e.Email,
            IsActive=bool(e.IsActive),
        )

    def delete_provider(self, db: Session, provider_id: int) -> bool:
        try:
            e = db.query(Provider).filter(Provider.Id == provider_id).first()
            if not e:
                return False
            db.delete(e)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
