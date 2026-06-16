import cloudinary.uploader


def upload_issue_image(image_path: str):

    result = cloudinary.uploader.upload(
        image_path,
        folder="issue_images"
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"]
    }