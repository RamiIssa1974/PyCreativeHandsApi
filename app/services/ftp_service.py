# app/services/ftp_service.py
import io
from ftplib import FTP
from typing import List, Optional
from fastapi import UploadFile
from app.core.config import get_settings  # same place your other settings come from

class FtpService:
    def __init__(self):
        s = get_settings()
        self.host = getattr(s, "FTP_HOST", None)
        self.user = getattr(s, "FTP_USER", None)
        self.password = getattr(s, "FTP_PASS", None)
        self.base_dir = getattr(s, "FTP_BASE_DIR", "") or ""

    def _connect(self) -> FTP:
        ftp = FTP(self.host, timeout=30)
        ftp.login(self.user, self.password)
        if self.base_dir:
            ftp.cwd(self.base_dir)
        return ftp

    async def upload_to_ftp(self, file: UploadFile, new_name: str, folder: str) -> Optional[str]:
        data = await file.read()
        bio = io.BytesIO(data)
        ftp = self._connect()
        try:
            try:
                ftp.mkd(folder)
            except Exception:
                pass
            ftp.cwd(folder)
            ftp.storbinary(f"STOR {new_name}", bio)
            return new_name
        finally:
            try:
                ftp.quit()
            except Exception:
                pass

    async def list_files_from_ftp(self, folder: str, product_id: int) -> List[str]:
        ftp = self._connect()
        try:
            ftp.cwd(folder)
            files = ftp.nlst()
            pref = f"prod_{product_id}_"
            return [f for f in files if f.lower().startswith(pref.lower())]
        finally:
            try:
                ftp.quit()
            except Exception:
                pass

    async def delete_files_from_ftp(self, files: List[str], folder: str) -> List[str]:
        failed: List[str] = []
        ftp = self._connect()
        try:
            ftp.cwd(folder)
            for f in files:
                try:
                    ftp.delete(f)
                except Exception:
                    failed.append(f)
            return failed
        finally:
            try:
                ftp.quit()
            except Exception:
                pass
