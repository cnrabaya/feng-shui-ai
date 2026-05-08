import base64
from pathlib import Path

import pytest

from app.services.vision import VisionService
from app.services.merge import MergeService
from app.core.utils import process_image_base64
from app.core.config import settings


@pytest.fixture
def real_vision_service():
    return VisionService()


@pytest.fixture
def real_merge_service():
    return MergeService()


def _load_asset(name: str) -> str:
    path = Path(__file__).parent.parent / "assets" / name
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@pytest.fixture
def room_1_base64():
    return _load_asset("room_1.png")


@pytest.fixture
def room_2_base64():
    return _load_asset("room_2.png")


@pytest.fixture
def room_1_processed_base64(room_1_base64):
    return process_image_base64(room_1_base64)


@pytest.fixture
def room_2_processed_base64(room_2_base64):
    return process_image_base64(room_2_base64)