# app/repositories/upload_repository.py
import os
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

# USE YOUR EXISTING IMAGE MODEL
from app.models_sql.image import SqlImage            # <-- your file/class
from app.models_sql.purchase_image import SqlPurchaseImage
# For auto-creating product when productId <= 0:
from app.models_sql.product import SqlProduct      # assumes you have this (Id, Name, Price)
from app.schemas.upload import UploadFilesResponse
from app.services.ftp_service import FtpService

class UploadRepository:
    def __init__(self, ftp: Optional[FtpService] = None):
        self._ftp = ftp or FtpService()

    def _ftp_sync_upload(self, file: UploadFile, name: str, folder: str) -> Optional[str]:
        import anyio
        return anyio.run(self._ftp.upload_to_ftp, file, name, folder)

    def _ftp_sync_list(self, folder: str, product_id: int) -> List[str]:
        import anyio
        return anyio.run(self._ftp.list_files_from_ftp, folder, product_id)

    def _ftp_sync_delete(self, files: List[str], folder: str) -> List[str]:
        import anyio
        return anyio.run(self._ftp.delete_files_from_ftp, files, folder)

    # ---------- UploadFiles (product) ----------
    def upload_file(self, db: Session, file: UploadFile, product_id: int) -> UploadFilesResponse:
        if file is None:
            return UploadFilesResponse(VideoId=-1, ProductId=-1, PurchaseId=-1, UploadedImages=None)

        resp = UploadFilesResponse(VideoId=0, ProductId=product_id, PurchaseId=0, UploadedImages=[])

        # Create product if needed (like C# repository)
        if product_id <= 0:
            p = SqlProduct(Name="", Price=0)
            db.add(p)
            db.flush()
            product_id = p.Id
            resp.ProductId = product_id

        # Create Image row to get Id-based filename
        ext_with_dot = os.path.splitext(file.filename or "")[1]  # ".jpg"
        ext = ext_with_dot[1:] if ext_with_dot.startswith(".") else ext_with_dot

        img = SqlImage(ProductId=product_id, Extension=ext or "")
        db.add(img)
        db.flush()
        file_name = f"{img.Id}{ext_with_dot}"

        uploaded = self._ftp_sync_upload(file, file_name, "Images")
        if uploaded:
            resp.UploadedImages.append(uploaded)

        db.commit()
        return resp

    # ---------- UploadPurchaseFile ----------
    def upload_purchase_file(self, db: Session, file: UploadFile, purchase_id: int) -> UploadFilesResponse:
        if file is None or purchase_id <= 0:
            return UploadFilesResponse(VideoId=-1, ProductId=-1, PurchaseId=-1, UploadedImages=None)

        resp = UploadFilesResponse(VideoId=0, ProductId=0, PurchaseId=purchase_id, UploadedImages=[])

        ext_with_dot = os.path.splitext(file.filename or "")[1]
        pi = db.query(SqlPurchaseImage).filter(SqlPurchaseImage.PurchaseId == purchase_id).first()
        if not pi:
            pi = SqlPurchaseImage(PurchaseId=purchase_id, Extension=(ext_with_dot[1:] if ext_with_dot.startswith(".") else ""))
            db.add(pi)
            db.flush()

        file_name = f"{pi.Id}{ext_with_dot}"
        uploaded = self._ftp_sync_upload(file, file_name, "Images/Purchases")
        if uploaded:
            resp.UploadedImages.append(uploaded)

        db.commit()
        return resp

    # ---------- UploadFilesFromUmbraco (bulk) ----------
    def upload_umbraco_files(self, db: Session, files: List[UploadFile], product_id: int) -> UploadFilesResponse:
        resp = UploadFilesResponse(VideoId=0, ProductId=product_id, PurchaseId=0, UploadedImages=[])

        if not files:
            return resp

        # Delete existing prod_{productId}_*.*
        existing = self._ftp_sync_list("Images/Umbraco", product_id)
        if existing:
            self._ftp_sync_delete(existing, "Images/Umbraco")

        # Upload sequentially with the required naming
        i = 1
        for f in files:
            ext = os.path.splitext(f.filename or "")[1]
            new_name = f"prod_{product_id}_{i}{ext}"
            uploaded = self._ftp_sync_upload(f, new_name, "Images/Umbraco")
            if uploaded:
                resp.UploadedImages.append(uploaded)
            i += 1

        return resp
