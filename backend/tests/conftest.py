import pytest
from pathlib import Path

from app.models.schemas import MultiImageData
from tests.helpers import load_and_encode_image


@pytest.fixture
def assets_dir():
    return Path(__file__).parent / "assets"


@pytest.fixture
def sample_image(assets_dir: Path):
    image_path = assets_dir / "room_1.jpg"
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return load_and_encode_image(image_path)


@pytest.fixture
def sample_images(assets_dir: Path):
    image_files = sorted(assets_dir.glob("room_*.jpg"))
    if not image_files:
        pytest.skip(f"No test images found in {assets_dir}")
    result = []
    for f in image_files:
        base64_img = load_and_encode_image(f)
        result.append(MultiImageData(image=base64_img, direction="not_sure"))
    return result


@pytest.fixture
def sample_images_with_direction(assets_dir: Path):
    image_files = sorted(assets_dir.glob("room_*.jpg"))
    if len(image_files) < 2:
        pytest.skip(f"Need at least 2 test images in {assets_dir}")
    directions = ["north", "south"]
    result = []
    for i, f in enumerate(image_files[:2]):
        base64_img = load_and_encode_image(f)
        result.append(MultiImageData(image=base64_img, direction=directions[i]))
    return result