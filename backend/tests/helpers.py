import base64
import io
from pathlib import Path

from PIL import Image

from app.services.image_processor import fix_rotation, prepare_for_upload


def load_and_encode_image(path: Path, max_dimension: int = 1920) -> str:
    img = Image.open(path)
    img = fix_rotation(img)
    img = prepare_for_upload(img, max_dimension=max_dimension)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")