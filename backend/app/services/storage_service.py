from pathlib import Path
import logging
from io import BytesIO
import shutil
import os


class StorageService:
    def __init__(self, upload_dir: str = "static/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"StorageService initialized at {self.upload_dir}")

    # ============================
    # Upload file
    # ============================
    def upload_file(self, file_data: BytesIO, object_name: str) -> None:
        """
        Lưu file vật lý vào static/uploads
        ⚠️ KHÔNG trả về URL
        ⚠️ DB chỉ lưu filename
        """
        file_path = self.upload_dir / object_name

        with file_path.open("wb") as f:
            shutil.copyfileobj(file_data, f)

    # ============================
    # Delete file
    # ============================
    def delete_file(self, image_url_or_name: str) -> bool:
        """
        Nhận:
        - filename (abc.jpg)
        - hoặc /static/uploads/abc.jpg

        → tự xử lý để xóa file vật lý
        """
        try:
            filename = os.path.basename(image_url_or_name)
            file_path = self.upload_dir / filename

            if file_path.exists():
                file_path.unlink()

            return True
        except Exception as e:
            logging.error(f"Delete file error: {e}")
            return False


storage_service = StorageService()
