import base64
import io
import os
import tempfile
import pytest
from PIL import Image, ImageOps

from app.core.utils import fix_rotation, prepare_for_upload, process_image_base64


def make_image(width: int, height: int, mode: str = "RGB") -> Image.Image:
    return Image.new(mode, (width, height), color=(128, 128, 128))


def image_to_bytes(img: Image.Image, format: str = "JPEG") -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


class TestPrepareForUpload:
    def test_no_resize_when_small(self):
        img = make_image(800, 600)
        result = prepare_for_upload(img, max_dimension=1920)
        assert result.size == (800, 600)

    def test_resizes_oversized_image(self):
        img = make_image(4000, 3000)
        result = prepare_for_upload(img, max_dimension=1920)
        assert max(result.size) == 1920
        assert result.size[0] <= 1920 and result.size[1] <= 1920

    def test_preserves_aspect_ratio(self):
        img = make_image(4000, 2000)
        result = prepare_for_upload(img, max_dimension=1920)
        assert result.size[0] == 1920
        assert result.size[1] == 960

    def test_exactly_at_max_no_change(self):
        img = make_image(1920, 1080)
        result = prepare_for_upload(img, max_dimension=1920)
        assert result.size == (1920, 1080)

    def test_square_image_resizes(self):
        img = make_image(3000, 3000)
        result = prepare_for_upload(img, max_dimension=1920)
        assert max(result.size) == 1920


class TestFixRotation:
    def test_image_without_exif_returns_same_dimensions(self):
        img = make_image(100, 100)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            img.save(f, format="JPEG")
        try:
            result = fix_rotation(f.name)
            assert result.size == (100, 100)
        finally:
            os.unlink(f.name)

    def test_fix_rotation_produces_valid_image(self):
        img = make_image(100, 200)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            img.save(f, format="JPEG")
        try:
            result = fix_rotation(f.name)
            assert result is not None
            assert hasattr(result, "size")
            assert result.size[0] > 0 and result.size[1] > 0
        finally:
            os.unlink(f.name)


class TestProcessImageBase64:
    def test_rgba_to_rgb_conversion(self):
        img = Image.new("RGBA", (100, 100), color=(128, 64, 32, 255))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        result_b64 = process_image_base64(b64)
        result_bytes = base64.b64decode(result_b64)
        result_img = Image.open(io.BytesIO(result_bytes))

        assert result_img.mode == "RGB"
        assert result_img.size == (100, 100)

    def test_preserves_small_image_dimensions(self):
        img = Image.new("RGB", (800, 600), color=(100, 100, 100))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        result_b64 = process_image_base64(b64)
        result_bytes = base64.b64decode(result_b64)
        result_img = Image.open(io.BytesIO(result_bytes))

        assert result_img.size == (800, 600)

    def test_resizes_oversized_image(self):
        img = Image.new("RGB", (4000, 3000), color=(100, 100, 100))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        result_b64 = process_image_base64(b64)
        result_bytes = base64.b64decode(result_b64)
        result_img = Image.open(io.BytesIO(result_bytes))

        assert max(result_img.size) == 1920
        assert result_img.size[0] <= 1920
        assert result_img.size[1] <= 1920

    def test_png_input_produces_valid_jpeg(self):
        img = Image.new("RGB", (200, 150), color=(50, 100, 150))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        result_b64 = process_image_base64(b64)
        result_bytes = base64.b64decode(result_b64)
        result_img = Image.open(io.BytesIO(result_bytes))

        assert result_img.format == "JPEG"
        assert result_img.mode == "RGB"
        assert result_img.size == (200, 150)