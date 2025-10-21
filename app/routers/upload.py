# app/routers/upload.py
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.db.session_sql import get_db
from app.repositories.upload_repository import UploadRepository
from app.schemas.upload import UploadFilesResponse

router = APIRouter()
_repo = UploadRepository()

# ---- UploadFiles ----
@router.post("/Api/UploadFiles")
@router.post("/api/UploadFiles")
@router.post("/UploadFiles")
@router.post("/uploadfiles")
async def upload_files(
    files: List[UploadFile] = File(...),
    productId: int = Form(..., alias="productId"),
    db: Session = Depends(get_db),
) -> UploadFilesResponse:
    if not files or files[0] is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files were uploaded.")
    resp = await run_in_threadpool(_repo.upload_file, db, files[0], productId)
    if resp is None or resp.UploadedImages is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem occured while Uploading the file.")
    return resp

# ---- UploadPurchaseFile ----
@router.post("/Api/UploadPurchaseFile")
@router.post("/api/UploadPurchaseFile")
@router.post("/UploadPurchaseFile")
@router.post("/uploadpurchasefile")
async def upload_purchase_file(
    file: UploadFile = File(...),
    purchaseId: int = Form(..., alias="purchaseId"),
    db: Session = Depends(get_db),
) -> UploadFilesResponse:
    if file is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file.")
    if purchaseId <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid purchase ID.")
    resp = await run_in_threadpool(_repo.upload_purchase_file, db, file, purchaseId)
    if resp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No purchases found for the given purchase ID.")
    return resp

# ---- UploadFilesFromUmbraco ----
@router.post("/Api/UploadFilesFromUmbraco")
@router.post("/api/UploadFilesFromUmbraco")
@router.post("/UploadFilesFromUmbraco")
@router.post("/uploadfilesfromumbraco")
async def upload_files_from_umbraco(
    files: List[UploadFile] = File(...),
    productId: int = Form(..., alias="productId"),
    db: Session = Depends(get_db),
) -> UploadFilesResponse:
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files were uploaded.")
    resp = await run_in_threadpool(_repo.upload_umbraco_files, db, files, productId)
    if resp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem occured while Uploading the file.")
    return resp
