"""
Manual E2E test script for the FengShuiAI vision pipeline.

Usage:
    # Single image
    uv run python tests/e2e/manual_test.py "path/to/room.png"

    # Single image with direction
    uv run python tests/e2e/manual_test.py "path/to/room.png" --direction north

    # Two images (merge)
    uv run python tests/e2e/manual_test.py "path/to/room1.png" "path/to/room2.png"
"""
import argparse
import asyncio
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.schemas import MultiImageData
from app.services.vision import VisionService
from app.services.merge import MergeService
from app.services.image_processor import process_image_base64


def load_image_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def test_single_image(image_path: str, direction: str | None = None):
    print(f"\n[Vision] Processing single image: {image_path}")
    if direction:
        print(f"[Vision] Direction: {direction}")

    raw_b64 = load_image_base64(image_path)
    processed = process_image_base64(raw_b64)
    print(f"[Vision] Image preprocessed ({len(processed):,} chars base64)")

    service = VisionService()
    result, llm_raw = await service.extract_elements(processed, direction=direction, return_raw=True)

    print(f"\n[LLM Raw Response]")
    print("-" * 60)
    print(llm_raw)
    print("-" * 60)

    print(f"\n[Vision] Extracted {len(result.elements)} element(s)")
    for e in result.elements:
        print(f"  - [{e.confidence}] {e.type}: {e.id}")

    if result.architectural_features:
        af = result.architectural_features
        print(f"\n[Vision] Architectural features:")
        print(f"  Doors: {af.doors}")
        print(f"  Windows: {af.windows}")
        print(f"  Visible walls: {af.visible_walls}")

    return result, llm_raw


async def test_batch_images(image_paths: list[str], directions: list[str | None]):
    print(f"\n[Vision] Processing {len(image_paths)} images in batch")

    images = []
    for path, direction in zip(image_paths, directions):
        raw = load_image_base64(path)
        processed = process_image_base64(raw)
        images.append(MultiImageData(image=processed, direction=direction or "not_sure"))
        print(f"[Vision]   {path} -> preprocessed ({len(processed):,} chars, direction={direction})")

    service = VisionService()
    results = await service.extract_elements_batch(images, return_raw=True)

    for i, r in enumerate(results):
        result, llm_raw = r
        print(f"\n[LLM Raw Response - Image {i+1}]")
        print("-" * 60)
        print(llm_raw)
        print("-" * 60)
        print(f"\n[Vision] Image {i+1} ({image_paths[i]}): {len(result.elements)} element(s)")
        for e in result.elements:
            print(f"  - [{e.confidence}] {e.type}: {e.id}")
        if result.architectural_features:
            af = result.architectural_features
            print(f"  Doors: {af.doors}, Windows: {af.windows}, Walls: {af.visible_walls}")

    return results


async def test_merge(image_paths: list[str], directions: list[str | None]):
    print(f"\n[Merge] Extracting from {len(image_paths)} images first...")

    images = []
    for path, direction in zip(image_paths, directions):
        raw = load_image_base64(path)
        processed = process_image_base64(raw)
        images.append(MultiImageData(image=processed, direction=direction or "not_sure"))

    vision = VisionService()
    extractions = await vision.extract_elements_batch(images, return_raw=True)
    print(f"[Merge] Got {len(extractions)} extractions")

    for i, (result, llm_raw) in enumerate(extractions):
        print(f"\n[LLM Raw Response - Image {i+1}]")
        print("-" * 60)
        print(llm_raw)
        print("-" * 60)

    parsed = [e[0] for e in extractions]
    merge = MergeService()
    merged = await merge.merge_results(parsed)

    print(f"\n[Merge] Confirmed elements ({len(merged.confirmed_elements)}):")
    for e in merged.confirmed_elements:
        print(f"  - {e.type}: {e.id} (confidence: {e.confidence})")

    print(f"\n[Merge] Unconfirmed elements ({len(merged.unconfirmed_elements)}):")
    for e in merged.unconfirmed_elements:
        print(f"  - {e.type}: {e.id} (confidence: {e.confidence})")

    if merged.spatial_conflicts:
        print(f"\n[Merge] Spatial conflicts ({len(merged.spatial_conflicts)}):")
        for c in merged.spatial_conflicts:
            print(f"  - {c.get('element_1')} vs {c.get('element_2')}: {c.get('description')}")

    if merged.architectural_features:
        af = merged.architectural_features
        print(f"\n[Merge] Merged architectural features:")
        print(f"  Doors: {af.doors}")
        print(f"  Windows: {af.windows}")
        print(f"  Visible walls: {af.visible_walls}")

    return merged


async def main():
    parser = argparse.ArgumentParser(description="Manual E2E test for FengShuiAI vision pipeline")
    parser.add_argument("images", nargs="+", help="Path to image file(s)")
    parser.add_argument("--direction", "-d", action="append", help="Direction per image (north/south/east/west)")
    parser.add_argument("--merge", "-m", action="store_true", help="Merge multiple images")

    args = parser.parse_args()

    if len(args.images) > 1 and args.merge:
        await test_merge(args.images, args.direction or ["not_sure"] * len(args.images))
    elif len(args.images) > 1:
        directions = args.direction or ["not_sure"] * len(args.images)
        await test_batch_images(args.images, directions)
    else:
        direction = args.direction[0] if args.direction else None
        await test_single_image(args.images[0], direction)

    print("\n[Done]")


if __name__ == "__main__":
    asyncio.run(main())