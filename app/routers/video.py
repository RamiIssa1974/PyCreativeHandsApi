# app/routers/video.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Body
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.db.session_sql import get_db
from app.repositories.video_repository import VideoRepository
from app.schemas.video import VideoModel, VideoModelIn
from app.schemas.upload import UploadFilesResponse

router = APIRouter()
_repo = VideoRepository()


# -------- GetVideos (POST body: VideoModel) --------
@router.post("/Videos")
async def get_videos(
    request: VideoModelIn = Body(...),
    db: Session = Depends(get_db)
) -> List[VideoModel]:
    if request is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request.")
    res = await run_in_threadpool(_repo.get_videos, db, request)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No videos found matching the given criteria.")
    return res


# -------- SaveVideo (multipart: file + fields) --------
@router.post("/SaveVideo")
async def save_video(
    file: UploadFile = File(...),
    Id: int = Form(-1),
    VideoName: str = Form(...),
    Extension: Optional[str] = Form(None),
    Title: Optional[str] = Form(None),
    Description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> UploadFilesResponse:
    
    if file is None or (hasattr(file, "size") and file.size == 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file.")

    req = VideoModelIn(Id=Id, VideoName=VideoName, Extension=Extension, Title=Title, Description=Description)
    if req is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request.")

    resp = await run_in_threadpool(_repo.save_video, db, file, req)
    if resp is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while saving the video.")
    return resp


# -------- SaveVideoNew (multipart: file + fields) --------
@router.post("/SaveVideoNew")
async def save_video_new(
    file: UploadFile = File(...),
    Id: int = Form(-1),
    VideoName: str = Form(...),
    Extension: Optional[str] = Form(None),
    Title: Optional[str] = Form(None),
    Description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> UploadFilesResponse:
    if file is None or (hasattr(file, "size") and file.size == 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file.")

    req = VideoModelIn(Id=Id, VideoName=VideoName, Extension=Extension, Title=Title, Description=Description)
    if req is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request.")

    resp = await run_in_threadpool(_repo.save_video, db, file, req)
    if resp is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while saving the video.")
    return resp


# -------- DeleteVideo --------
@router.delete("/DeleteVideo/{videoId}")
async def delete_video(videoId: int, db: Session = Depends(get_db)):
    try:
        res = await run_in_threadpool(_repo.delete_video, db, videoId)
        if res:
            return f"Video with ID {videoId} deleted."
        else:
            # .NET returns 400 when not found (not 404)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Video with ID {videoId} not found.")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error, Deleting Video: {videoId}")
