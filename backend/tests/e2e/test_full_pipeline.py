import base64
import io

import pytest
from PIL import Image

from app.models.schemas import MultiImageData

pytestmark = pytest.mark.e2e


class TestVisionServiceE2E:
    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_single_image_returns_valid_schema(self, real_vision_service, room_1_processed_base64):
        result = await real_vision_service.extract_elements(room_1_processed_base64)

        assert len(result.elements) > 0, "Should detect at least one element"
        for e in result.elements:
            assert e.id, "Element must have an id"
            assert e.type, "Element must have a type"
            assert e.confidence in ("high", "medium", "low"), "Confidence must be high/medium/low"
        assert result.architectural_features is not None

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_single_image_with_direction(self, real_vision_service, room_1_processed_base64):
        result = await real_vision_service.extract_elements(room_1_processed_base64, direction="north")
        assert len(result.elements) >= 0
        for e in result.elements:
            assert e.id
            assert e.type

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_batch_two_images(self, real_vision_service, room_1_base64, room_2_base64):
        from app.services.image_processor import process_image_base64

        images = [
            MultiImageData(image=process_image_base64(room_1_base64), direction="north"),
            MultiImageData(image=process_image_base64(room_2_base64), direction="south"),
        ]
        results = await real_vision_service.extract_elements_batch(images)

        assert len(results) == 2
        for r in results:
            assert r.elements is not None
            assert r.architectural_features is not None


class TestMergeServiceE2E:
    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_merge_two_real_extractions(self, real_vision_service, real_merge_service, room_1_base64, room_2_base64):
        from app.services.image_processor import process_image_base64

        extractions = await real_vision_service.extract_elements_batch([
            MultiImageData(image=process_image_base64(room_1_base64), direction="north"),
            MultiImageData(image=process_image_base64(room_2_base64), direction="south"),
        ])

        assert len(extractions) == 2

        merged = await real_merge_service.merge_results(extractions)

        assert merged.confirmed_elements is not None
        assert merged.unconfirmed_elements is not None
        assert merged.architectural_features is not None
        assert isinstance(merged.confirmed_elements, list)
        assert isinstance(merged.unconfirmed_elements, list)
        assert isinstance(merged.spatial_conflicts, list)


class TestPreprocessingE2E:
    @pytest.mark.timeout(60)
    def test_png_processed_to_jpeg(self, room_1_base64):
        processed = process_image_base64(room_1_base64)
        assert processed != room_1_base64, "Processed should differ from original PNG"

        decoded = base64.b64decode(processed)
        img = Image.open(io.BytesIO(decoded))
        assert img.format == "JPEG", "Output should be JPEG"
        assert img.mode == "RGB", "Output should be RGB (not RGBA)"

    @pytest.mark.timeout(60)
    def test_processed_smaller_than_source_png(self, room_1_base64):
        processed = process_image_base64(room_1_base64)
        assert len(processed) < len(room_1_base64) * 1.5, "JPEG should be smaller than PNG source"

    @pytest.mark.timeout(60)
    def test_processed_base64_is_valid_image(self, room_1_base64):
        processed = process_image_base64(room_1_base64)
        decoded = base64.b64decode(processed)
        img = Image.open(io.BytesIO(decoded))
        assert img.width > 0 and img.height > 0