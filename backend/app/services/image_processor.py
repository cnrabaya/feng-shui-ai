import base64
import io

from PIL import Image, ImageOps


def fix_rotation(image_path):
    img = Image.open(image_path)
    return ImageOps.exif_transpose(img)


def prepare_for_upload(img, max_dimension=1920):
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    return img


def process_image_base64(base64_str: str, max_dimension: int = 1920) -> str:
    image_bytes = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    img = prepare_for_upload(img, max_dimension=max_dimension)
    if img.mode == "RGBA":
        img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
