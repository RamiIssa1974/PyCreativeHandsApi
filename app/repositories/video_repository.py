# app/repositories/video_repository.py
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models_sql.video import SqlVideo
from app.schemas.video import VideoModel, VideoModelIn
from app.schemas.upload import UploadFilesResponse
from app.services.ftp_service import FtpService
from app.utils.strings import to_valid_camel_case_file_name


class VideoRepository:
    def __init__(self, ftp: Optional[FtpService] = None):
        self._ftp = ftp or FtpService()

    # ---------- GetVideos ----------
    def get_videos(self, db: Session, request: VideoModelIn) -> Optional[List[VideoModel]]:
        q = db.query(SqlVideo)

        if request.Id is not None and request.Id != -1:
            q = q.filter(SqlVideo.Id == request.Id)
        if request.VideoName:
            q = q.filter(SqlVideo.Name.contains(request.VideoName))
        if request.Title:
            q = q.filter(SqlVideo.Title.contains(request.Title))
        if request.Description:
            q = q.filter(SqlVideo.Description.contains(request.Description))

        rows = q.all()
        if not rows:
            return None

        return [
            VideoModel(
                Id=r.Id,
                VideoName=r.Name,
                Extension=r.Extension,
                Title=r.Title,
                Description=r.Description,
            )
            for r in rows
        ]

    # ---------- SaveVideo / SaveVideoNew (same logic) ----------
    def save_video(self, db: Session, file: UploadFile, request: VideoModelIn) -> Optional[UploadFilesResponse]:
        # C# returns 500 (router) if repo returns null; we return valid response on success else None
        if file is None or (hasattr(file, "size") and file.size == 0):
            return None

        # Produce filename
        trimmed = to_valid_camel_case_file_name(request.VideoName or "")
        ext_with_dot = os.path.splitext(file.filename or "")[1]  # ".mp4" etc.
        if not ext_with_dot:
            return None
        file_name = f"{trimmed}{ext_with_dot}"

        # Insert or update SqlVideo
        if request.Id is None or request.Id <= 0:
            sql = SqlVideo(
                Name=trimmed,
                Extension=ext_with_dot.lstrip("."),
                Title=request.Title,
                Description=request.Description,
            )
            db.add(sql)
            db.flush()
            video_id = sql.Id
        else:
            sql = db.query(SqlVideo).filter(SqlVideo.Id == request.Id).first()
            if not sql:
                # create if not found? C# updates only if exists; otherwise nothing. We'll mimic: no create here.
                return None
            sql.Name = request.VideoName or sql.Name
            sql.Title = request.Title
            sql.Description = request.Description
            # In C# update branch, Extension set from request.Extension (not from file)
            if request.Extension:
                sql.Extension = request.Extension
            db.flush()
            video_id = sql.Id

        # Upload to FTP folder "videos" (lowercase, as in C# SaveVideo)
        uploaded = self._ftp_sync_upload(file, file_name, "videos")
        resp = UploadFilesResponse(VideoId=video_id, ProductId=0, PurchaseId=0, UploadedImages=[])
        if uploaded:
            resp.UploadedImages.append(uploaded)

        db.commit()
        return resp

    # ---------- DeleteVideo ----------
    def delete_video(self, db: Session, video_id: int) -> bool:
        v = db.query(SqlVideo).filter(SqlVideo.Id == video_id).first()
        if not v:
            return False

        filename = f"{v.Name}.{v.Extension}" if v.Name and v.Extension else None
        db.delete(v)
        db.commit()

        if filename:
            # C# deletes from "Videos" (capital V). Keep the same.
            failed = self._ftp_sync_delete([filename], "Videos")
            # ignore failures per C# (only logs); return True regardless
        return True

    # ---------- internal FTP sync helpers ----------
    def _ftp_sync_upload(self, file: UploadFile, name: str, folder: str) -> Optional[str]:
        import anyio
        return anyio.run(self._ftp.upload_to_ftp, file, name, folder)

    def _ftp_sync_delete(self, files: List[str], folder: str) -> List[str]:
        import anyio
        return anyio.run(self._ftp.delete_files_from_ftp, files, folder)
