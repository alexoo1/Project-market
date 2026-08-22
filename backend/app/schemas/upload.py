from pydantic import BaseModel


class UploadedImage(BaseModel):
    url: str


class UploadImagesResponse(BaseModel):
    images: list[UploadedImage]
