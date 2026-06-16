from transformers import (
    CLIPProcessor,
    CLIPModel
)
from PIL import Image
import torch

model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)


def get_image_embedding(image_path):

    image = Image.open(
        image_path
    ).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():
        features = model.get_image_features(
            **inputs
        )

    return (
        features[0]
        .cpu()
        .numpy()
        .tolist()
    )