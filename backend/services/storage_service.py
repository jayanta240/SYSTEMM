import cloudinary
import cloudinary.uploader
from config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_video(file_path: str):
    result = cloudinary.uploader.upload(
        file_path,
        resource_type="video"
    )
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"]
    }