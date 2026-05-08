"""
Manual E2E test script for the FengShuiAI pipeline.

Supports individual steps (vision, merge, layout, score) and the full pipeline.

Auto-loads config.toml from the same directory as this script.
Use --config to specify a different config file.

Usage:
    # Full pipeline from config (auto-loads config.toml)
    uv run python tests/e2e/manual_test.py

    # Full pipeline with config override
    uv run python tests/e2e/manual_test.py --config path/to/my_config.toml

    # Full pipeline on a single image (CLI overrides config)
    uv run python tests/e2e/manual_test.py evaluate path/to/room.png

    # Full pipeline with multiple photos + dimensions (CLI overrides config)
    uv run python tests/e2e/manual_test.py evaluate path/to/room1.png path/to/room2.png --dimensions 4.5x3.5 --grid-size 3x3

    # Vision extraction only (single image)
    uv run python tests/e2e/manual_test.py vision path/to/room.png --direction north

    # Merge only (2+ photos, no scoring)
    uv run python tests/e2e/manual_test.py merge path/to/room1.png path/to/room2.png

    # Layout only (after extraction, requires dimensions + grid-size)
    uv run python tests/e2e/manual_test.py layout path/to/room.png --dimensions 4.5x3.5 --grid-size 3x3

    # Score only (requires a session from a prior evaluate run)
    uv run python tests/e2e/manual_test.py score --session-id <id>

    # Full pipeline with school and birth date (CLI overrides config)
    uv run python tests/e2e/manual_test.py evaluate path/to/room.png --school form --birth-date 1990-01-15
"""
import argparse
import asyncio
import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-redef]

from app.core.utils import process_image_base64
from app.models.schemas import MultiImageData, Dimensions
from app.services.vision import VisionService
from app.services.merge import MergeService
from app.services.layout import layout_service
from app.services.scoring import scoring_service
from app.services.session import (
    store_extraction_result,
    store_merged_result,
    get_stored_elements_and_school,
)

VALID_FURNITURE_TYPES = {
    "bed", "sofa", "armchair", "dining_table", "coffee_table",
    "desk", "wardrobe", "dresser", "bookshelf", "tv_stand",
    "plant", "lamp_floor", "lamp_table", "lamp_ceiling",
    "mirror", "rug", "curtains", "artwork", "door", "window", "empty",
}


def parse_dimensions(value: str) -> Dimensions:
    match = re.match(r"^([0-9.]+)[xX]([0-9.]+)$", value.strip())
    if not match:
        raise ValueError(f"Invalid dimensions format: {value!r}. Expected LxW (e.g. 4.5x3.5)")
    return Dimensions(length=float(match.group(1)), width=float(match.group(2)))


def load_config(config_path: Path | None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent / "config.toml"

    if not config_path.exists():
        return {}

    with open(config_path, "rb") as f:
        print(f"[Config] Loaded: {config_path}")
        return tomllib.load(f)


def merge_with_config(args: argparse.Namespace, config: dict) -> argparse.Namespace:
    merged = argparse.Namespace(**vars(args))

    if "room" in config:
        room = config["room"]

        if getattr(args, "images", None) is None or len(getattr(args, "images", []) or []) == 0:
            image_paths = [img["path"] for img in config.get("images", [])]
            if image_paths:
                merged.images = image_paths

        if getattr(args, "direction", None) is None:
            directions = [img.get("direction", "not_sure") for img in config.get("images", [])]
            if directions:
                merged.direction = directions

        if getattr(args, "dimensions", None) is None and "dimensions" in room:
            try:
                merged.dimensions = parse_dimensions(room["dimensions"])
            except ValueError:
                pass

        if not hasattr(merged, "grid_size") or getattr(merged, "grid_size", None) is None:
            if "grid_size" in room:
                merged.grid_size = room["grid_size"]

        if args.school == "black_hat" and "school" in room:
            merged.school = room["school"]

        if getattr(args, "birth_date", None) is None and "birth_date" in room:
            merged.birth_date = room["birth_date"]

        if getattr(args, "kua_number", None) is None and "kua_number" in room:
            merged.kua_number = room["kua_number"]

        if getattr(args, "building_date", None) is None and "building_date" in room:
            merged.building_date = room["building_date"]

    return merged


def _resolve_asset_path(path: str) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return Path(__file__).parent.parent / "assets" / path


def load_image_base64(path: str) -> str:
    resolved = _resolve_asset_path(path)
    with open(resolved, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def load_image(path: str) -> tuple[str, str]:
    raw = load_image_base64(path)
    processed = process_image_base64(raw)
    return processed, raw


def print_divider(title: str | None = None, char: str = "-", width: int = 60):
    if title:
        print(f"\n{'=' * width}")
        print(f"  {title}")
        print('=' * width)
    else:
        print(char * width)


def print_score(score: dict):
    print(f"\n[Score] Total: {score.get('total', 'N/A')} / 100")
    chi_flow = score.get("chi_flow", "unknown")
    print(f"[Score] Chi flow: {chi_flow}")

    breakdown = score.get("breakdown", {})
    if breakdown:
        print(f"\n[Score] Breakdown:")
        for category, data in breakdown.items():
            if isinstance(data, dict):
                s = data.get("score", "?")
                mx = data.get("max", "?")
                status = data.get("status", "")
                print(f"  {category:30s}  {s:>3}/{mx:<3}  [{status}]")
            else:
                print(f"  {category:30s}  {data}")

    issues = score.get("issues", [])
    if issues:
        print(f"\n[Score] Issues ({len(issues)}):")
        for issue in issues:
            print(f"  - [{issue.get('zone', '?')}] {issue.get('issue', '?')}  (impact: {issue.get('score_impact', 0)})")

    overall = score.get("overall_assessment")
    if overall:
        print(f"\n[Score] Overall: {overall}")


def print_elements(elements: list, label: str = "Elements"):
    print(f"\n[{label}] {len(elements)} detected:")
    for e in elements:
        pos = e.get("position_relative_to_camera", "?") if isinstance(e, dict) else getattr(e, "position_relative_to_camera", "?")
        conf = e.get("confidence", "?") if isinstance(e, dict) else getattr(e, "confidence", "?")
        elem_type = e.get("type", "?") if isinstance(e, dict) else getattr(e, "type", "?")
        elem_id = e.get("id", "?") if isinstance(e, dict) else getattr(e, "id", "?")
        print(f"  - [{conf:6s}] {elem_type:20s}  {elem_id}  (pos: {pos})")


def print_room_grid(room_grid, length: float | None = None, width: float | None = None):
    if not room_grid or not room_grid.cells:
        print("[Layout] No grid generated")
        return
    grid_size_str = getattr(room_grid, "grid_size", "4x4")
    n = int(grid_size_str.split("x")[0])
    dims = f"{length}m x {width}m" if length and width else "dimensions unknown"
    print(f"\n[Layout] Room Grid ({dims}) — {grid_size_str} (top-left = north-west)")
    col_header = "  " + "  ".join(f"Col {i}  " for i in range(n))
    print(f"         {col_header}")
    sep = "       +" + "-------+" * n
    print(sep)
    for row in range(n):
        row_label = f"Row {row}"
        cells = [room_grid.cells.get(f"{row},{col}", "empty") for col in range(n)]
        print(f"  {row_label}  | " + " | ".join(f"{c:^5}" for c in cells) + " |")
        print(sep)


def print_architectural_features(af):
    if not af:
        return
    print(f"\n[Arch] Doors: {af.doors}")
    print(f"[Arch] Windows: {af.windows}")
    print(f"[Arch] Visible walls: {af.visible_walls}")


async def cmd_vision(image_paths: list[str], directions: list[str | None], dimensions: Dimensions | None):
    print_divider("Vision Extraction")
    images = []
    for path, direction in zip(image_paths, directions):
        processed, _ = load_image(path)
        images.append(MultiImageData(image=processed, direction=direction or "not_sure"))
        print(f"[Vision] {path} -> processed, direction={direction or 'not_sure'}")

    service = VisionService()
    if len(images) == 1:
        result, llm_raw = await service.extract_elements(
            images[0].image, direction=images[0].direction, dimensions=dimensions, return_raw=True
        )
        print_divider("LLM Raw Response")
        print(llm_raw)
        print_divider()
        print_elements(result.elements)
        print_architectural_features(result.architectural_features)
        return result, None
    else:
        results = await service.extract_elements_batch(images, dimensions=dimensions, return_raw=True)
        for i, (result, llm_raw) in enumerate(results):
            print_divider(f"LLM Raw Response — Image {i+1}")
            print(llm_raw)
            print_divider()
            print_elements(result.elements, f"Image {i+1} Elements")
            print_architectural_features(result.architectural_features)
        return [r[0] for r in results], None


async def cmd_merge(image_paths: list[str], directions: list[str | None], dimensions: Dimensions | None):
    print_divider("Merge (Vision + Merge)")
    images = []
    for path, direction in zip(image_paths, directions):
        processed, _ = load_image(path)
        images.append(MultiImageData(image=processed, direction=direction or "not_sure"))
        print(f"[Merge] {path} -> processed, direction={direction or 'not_sure'}")

    vision = VisionService()
    extractions = await vision.extract_elements_batch(images, dimensions=dimensions, return_raw=True)
    print(f"\n[Merge] Extracted {len(extractions)} photo(s)")

    parsed = [e[0] for e in extractions]
    merger = MergeService()
    merged = await merger.merge_results(parsed)

    print(f"\n[Merge] Confirmed elements: {len(merged.confirmed_elements)}")
    for e in merged.confirmed_elements:
        print(f"  - {e.type}: {e.id}  (confidence: {e.confidence})")
    print(f"[Merge] Unconfirmed elements: {len(merged.unconfirmed_elements)}")
    for e in merged.unconfirmed_elements:
        print(f"  - {e.type}: {e.id}  (confidence: {e.confidence})")

    if merged.spatial_conflicts:
        print(f"\n[Merge] Spatial conflicts ({len(merged.spatial_conflicts)}):")
        for c in merged.spatial_conflicts:
            print(f"  - {c.get('element_1')} vs {c.get('element_2')}: {c.get('description')}")

    print_architectural_features(merged.architectural_features)
    return merged


async def cmd_layout(extraction_or_merged, dimensions: Dimensions | None, grid_size: str = "4x4"):
    print_divider("Layout Generation")
    if dimensions is None:
        print("[Layout] ERROR: --dimensions required for layout generation")
        return None

    if hasattr(extraction_or_merged, "model_dump_json"):
        json_data = extraction_or_merged.model_dump_json(indent=2)
    else:
        json_data = extraction_or_merged

    grid = await layout_service.generate_grid(json_data, dimensions, grid_size=grid_size)
    print_room_grid(grid, dimensions.length, dimensions.width)
    return grid


async def cmd_score(elements: list, school: str, dimensions: Dimensions | None, birth_date: str | None, kua_number: int | None):
    print_divider(f"Scoring ({school})")
    result = await scoring_service.score(
        elements=elements,
        school=school,
        dimensions=dimensions,
        birth_date=birth_date,
        kua_number=kua_number,
    )
    print_score(result)
    return result


async def cmd_evaluate(
    image_paths: list[str],
    directions: list[str | None],
    dimensions: Dimensions | None,
    school: str,
    birth_date: str | None,
    kua_number: int | None,
    building_date: str | None,
    grid_size: str = "4x4",
):
    """Full pipeline: vision -> merge -> layout -> score."""
    print_divider(f"Full Evaluate Pipeline")
    print(f"[Pipeline] Images: {len(image_paths)}")
    if dimensions:
        print(f"[Pipeline] Dimensions: {dimensions.length}m x {dimensions.width}m")
    print(f"[Pipeline] Grid size: {grid_size}")
    print(f"[Pipeline] School: {school}")
    if birth_date:
        print(f"[Pipeline] Birth date: {birth_date}")
    if kua_number:
        print(f"[Pipeline] Kua number: {kua_number}")

    images = []
    for path, direction in zip(image_paths, directions):
        processed, _ = load_image(path)
        images.append(MultiImageData(image=processed, direction=direction or "not_sure"))
        print(f"[Pipeline]   {path} -> processed, direction={direction or 'not_sure'}")

    vision = VisionService()

    if len(images) == 1:
        print_divider("Vision Extraction")
        result = await vision.extract_elements(images[0].image, direction=images[0].direction, dimensions=dimensions)
        print_elements(result.elements)
        print_architectural_features(result.architectural_features)

        elements = [
            {"id": e.id, "type": e.type, "position": e.position_relative_to_camera, "confidence": e.confidence}
            for e in result.elements
        ]
        merged = None
        room_grid = None

        if dimensions:
            grid = await cmd_layout(result, dimensions, grid_size=grid_size)
            room_grid = grid

    else:
        print_divider("Vision Batch Extraction")
        extractions = await vision.extract_elements_batch(images, dimensions=dimensions)
        print(f"[Pipeline] Got {len(extractions)} extractions")

        print_divider("Merge")
        merger = MergeService()
        merged = await merger.merge_results(extractions)
        print(f"[Merge] Confirmed: {len(merged.confirmed_elements)}, Unconfirmed: {len(merged.unconfirmed_elements)}")

        for e in merged.confirmed_elements:
            print(f"  - {e.type}: {e.id}")
        if merged.unconfirmed_elements:
            print("  (unconfirmed):")
            for e in merged.unconfirmed_elements:
                print(f"  - {e.type}: {e.id}")

        elements = [
            {"id": e.id, "type": e.type, "position": e.position_relative_to_camera, "confidence": e.confidence}
            for e in merged.confirmed_elements + merged.unconfirmed_elements
        ]
        room_grid = None

        if dimensions:
            grid = await cmd_layout(merged, dimensions, grid_size=grid_size)
            room_grid = grid

    print_divider(f"Scoring ({school})")
    score_result = await scoring_service.score(
        elements=elements,
        school=school,
        dimensions=dimensions,
        birth_date=birth_date,
        kua_number=kua_number,
        building_date=building_date,
    )
    print_score(score_result)

    print_divider("Pipeline Complete")
    print(f"  Elements:      {len(elements)}")
    print(f"  Room grid:     {'generated' if room_grid else 'not generated'}")
    print(f"  Score:         {score_result.get('total_score', score_result.get('total', 'N/A'))}/100")
    print(f"  Chi flow:      {score_result.get('chi_flow', 'N/A')}")

    return {
        "elements": elements,
        "room_grid": room_grid,
        "score": score_result,
        "dimensions": dimensions,
    }


def parse_grid_size(value: str) -> str:
    match = re.match(r"^(\d+)x(\d+)$", value.strip())
    if not match:
        raise ValueError(f"Invalid grid_size format: {value!r}. Expected 'NxN' (e.g. '3x3', '4x4', '5x5')")
    n = int(match.group(1))
    if n < 1 or n > 10:
        raise ValueError(f"grid_size N must be 1..10, got {n}")
    if match.group(1) != match.group(2):
        raise ValueError(f"grid_size must be 'NxN', got {value!r}")
    return f"{n}x{n}"


async def main():
    parser = argparse.ArgumentParser(
        description="Manual E2E test for FengShuiAI full pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  vision    Vision extraction only (single image or batch)
  merge     Vision + merge (2+ images, no scoring)
  layout    Layout generation only (requires --dimensions + --grid-size)
  score     Score a stored session (requires --session-id)
  evaluate  Full pipeline: vision -> merge -> layout -> score (default)

Config:
  Config file (config.toml) is auto-loaded from the same directory as this script.
  Config values override CLI defaults. Run without arguments to use config.

Examples:
  uv run python tests/e2e/manual_test.py                         # uses config.toml
  uv run python tests/e2e/manual_test.py evaluate room.png       # CLI image overrides config
  uv run python tests/e2e/manual_test.py evaluate room1.png room2.png --dimensions 4.5x3.5 --grid-size 3x3
  uv run python tests/e2e/manual_test.py merge room1.png room2.png
  uv run python tests/e2e/manual_test.py score --session-id abc123
        """,
    )
    parser.add_argument(
        "command",
        choices=["vision", "merge", "layout", "score", "evaluate"],
        nargs="?",
        default="evaluate",
        help="Pipeline step to run (default: evaluate)",
    )
    parser.add_argument("images", nargs="*", help="Path to image file(s)")
    parser.add_argument("--direction", "-d", action="append", help="Direction per image (north/south/east/west)")
    parser.add_argument("--dimensions", "-dim", type=str, help="Room dimensions (e.g. 4.5x3.5)")
    parser.add_argument("--grid-size", "-g", type=str, default=None, help="Grid size as 'NxN' (e.g. '3x3', '4x4', up to '10x10')")
    parser.add_argument("--school", "-s", default="black_hat",
                        choices=["black_hat", "form", "three_door", "five_elements", "compass"],
                        help="Feng Shui school (default: black_hat)")
    parser.add_argument("--birth-date", type=str, help="Birth date for Eight Mansions (YYYY-MM-DD)")
    parser.add_argument("--kua-number", type=int, help="Kua number (1-9) for Eight Mansions")
    parser.add_argument("--building-date", type=str, help="Building date for Flying Star (YYYY-MM-DD)")
    parser.add_argument("--session-id", type=str, help="Session ID for score command")
    parser.add_argument("--config", "-c", type=str, help="Path to config.toml (default: config.toml next to this script)")

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None
    config = load_config(config_path)
    args = merge_with_config(args, config)

    dimensions = None
    if getattr(args, "dimensions", None) is not None:
        if isinstance(args.dimensions, str):
            try:
                dimensions = parse_dimensions(args.dimensions)
            except ValueError as e:
                print(f"[Error] {e}")
                sys.exit(1)
        elif hasattr(args.dimensions, "length"):
            dimensions = args.dimensions

    grid_size = "4x4"
    if getattr(args, "grid_size", None):
        try:
            grid_size = parse_grid_size(args.grid_size)
        except ValueError as e:
            print(f"[Error] {e}")
            sys.exit(1)

    directions = args.direction or ["not_sure"] * len(args.images) if args.images else []

    command = args.command

    if command == "score":
        if not args.session_id:
            print("[Error] --session-id required for score command")
            sys.exit(1)
        stored = get_stored_elements_and_school(args.session_id)
        if not stored:
            print(f"[Error] Session {args.session_id} not found")
            sys.exit(1)
        elements, stored_school = stored
        school = args.school or stored_school
        score_result = await scoring_service.score(
            elements=elements,
            school=school,
            dimensions=dimensions,
            birth_date=args.birth_date,
            kua_number=args.kua_number,
            building_date=args.building_date,
        )
        print_divider(f"Score for Session {args.session_id} ({school})")
        print_score(score_result)
        return

    if not args.images:
        print("[Error] No images provided (set [[images]] in config.toml or pass as positional args). See --help.")
        sys.exit(1)

    if command == "vision":
        await cmd_vision(args.images, directions, dimensions)

    elif command == "merge":
        await cmd_merge(args.images, directions, dimensions)

    elif command == "layout":
        if not dimensions:
            print("[Error] --dimensions required for layout command")
            sys.exit(1)
        extraction, _ = await cmd_vision(args.images, directions, dimensions)
        await cmd_layout(extraction, dimensions, grid_size=grid_size)

    elif command == "evaluate":
        await cmd_evaluate(
            args.images,
            directions,
            dimensions,
            args.school,
            args.birth_date,
            args.kua_number,
            args.building_date,
            grid_size=grid_size,
        )

    print("\n[Done]")


if __name__ == "__main__":
    asyncio.run(main())