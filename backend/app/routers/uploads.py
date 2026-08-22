from fastapi import APIRouter, Depends, UploadFile

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.upload import UploadedImage, UploadImagesResponse
from app.services.storage.local_provider import get_storage_provider
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/images", response_model=UploadImagesResponse)
async def upload_images(
    files: list[UploadFile],
    current_user: User = Depends(get_current_user),
):
    service = UploadService(get_storage_provider())
    images = []
    for file in files:
        content = await file.read()
        url = service.save_image(content, file.content_type)
        images.append(UploadedImage(url=url))
    return UploadImagesResponse(images=images)
