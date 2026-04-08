from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.dependencies import require_active_user
from app.services.storage_service import storage_service
import uuid
from io import BytesIO

router = APIRouter(prefix="/api/v1/upload", tags=["Upload"])


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    _=Depends(require_active_user)
):
    ext = file.filename.split(".")[-1].lower()

    if ext not in ["png", "jpg", "jpeg", "gif"]:
        raise HTTPException(400, "File không hợp lệ")

    file_name = f"{uuid.uuid4()}.{ext}"
    file_data = BytesIO(await file.read())

    storage_service.upload_file(
        file_data=file_data,
        object_name=file_name,
        content_type=file.content_type
    )

    return {
        "file_name": file_name,
        "url": f"/static/uploads/{file_name}"
    }
