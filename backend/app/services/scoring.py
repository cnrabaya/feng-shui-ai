from typing import Optional
from app.models.schemas import ScoreBreakdown, Issue, Dimensions


FIVE_ELEMENTS = {
    "wood": ["plant", "wood", "bookshelf", "dresser", "wardrobe", "plant_1"],
    "fire": ["lamp", "lamp_floor", "lamp_table", "lamp_ceiling", "fireplace", "tv", "tv_stand", "electronics"],
    "earth": ["rug", "carpet", "curtains", "ceramics", "crystal", "stone"],
    "metal": ["mirror", "metal", "metal_furniture", "floor_lamp", "lamp_1"],
    "water": ["aquarium", "water_feature", "reflective_surface", "glass", "window"],
}

BAGUA_ZONES = {
    "wealth": ["southeast", "se"],
    "fame": ["south", "s"],
    "relationships": ["southwest", "sw"],
    "family": ["east", "e"],
    "health": ["center", "middle", "centre"],
    "creativity": ["west", "w"],
    "knowledge": ["northeast", "ne"],
    "career": ["north", "n"],
    "helpful_people": ["northwest", "nw"],
}

ZONE_FURNITURE = {
    "wealth": ["plant", "artwork", "mirror"],
    "fame": ["artwork", "lamp", "fireplace"],
    "relationships": ["mirror", "pairs", "love_symbol"],
    "family": ["plants", "green_items", "wood_furniture"],
    "health": ["plants", "light", "wood"],
    "creativity": ["artwork", "crystals", "metal_items"],
    "knowledge": ["bookshelf", "desk", "computer"],
    "career": ["mirror", "water_feature", "black_items"],
    "helpful_people": ["metal", "crystals", "round_shapes"],
}

PRIMARY_FURNITURE = ["bed", "sofa", "desk", "chair", "armchair"]
DIRECTION_OPPOSITES = {
    "north": "south", "south": "north", "east": "west", "west": "east",
    "northeast": "southwest", "southwest": "northeast",
    "southeast": "northwest", "northwest": "southeast",
    "ne": "sw", "sw": "ne", "se": "nw", "nw": "se",
}
WALLS = ["north", "south", "east", "west", "n", "s", "e", "w"]


def _get_element_type(element: dict) -> str:
    return element.get("type", "").lower()


def _get_element_position(element: dict) -> str:
    return element.get("position", "").lower()


def _get_element_orientation(element: dict) -> str:
    return element.get("orientation", "").lower()


def _extract_door_info(elements: list[dict]) -> list[dict]:
    doors = []
    for el in elements:
        if "door" in _get_element_type(el).lower():
            doors.append({
                "position": _get_element_position(el),
                "orientation": _get_element_orientation(el),
            })
    return doors


def _extract_windows(elements: list[dict]) -> list[dict]:
    windows = []
    for el in elements:
        etype = _get_element_type(el)
        if "window" in etype or "curtain" in etype:
            windows.append({
                "position": _get_element_position(el),
                "orientation": _get_element_orientation(el),
            })
    return windows


def _extract_mirrors(elements: list[dict]) -> list[dict]:
    mirrors = []
    for el in elements:
        if "mirror" in _get_element_type(el).lower():
            mirrors.append({
                "position": _get_element_position(el),
                "orientation": _get_element_orientation(el),
            })
    return mirrors


def _extract_beds(elements: list[dict]) -> list[dict]:
    return [el for el in elements if "bed" in _get_element_type(el).lower()]


def _get_primary_furniture(elements: list[dict]) -> list[dict]:
    return [el for el in elements if any(pf in _get_element_type(el).lower() for pf in PRIMARY_FURNITURE)]


def _position_contains(position: str, keywords: list[str]) -> bool:
    pos_lower = position.lower()
    return any(kw in pos_lower for kw in keywords)


def _infer_facing_direction(position: str, orientation: str) -> Optional[str]:
    if not position and not orientation:
        return None
    pos_lower = position.lower()
    for direction in ["north", "south", "east", "west", "n", "s", "e", "w",
                      "northeast", "northwest", "southeast", "southwest",
                      "ne", "nw", "se", "sw"]:
        if direction in pos_lower:
            return direction
        if direction in orientation.lower():
            return direction
    return None


def _door_in_facing_direction(furniture_pos: str, furniture_facing: str, doors: list[dict]) -> bool:
    if not doors:
        return False

    furniture_facing_dir = _infer_facing_direction(furniture_pos, furniture_facing)

    for door in doors:
        door_pos = door.get("position", "")
        door_facing = door.get("orientation", "")
        door_dir = _infer_facing_direction(door_pos, door_facing)

        if not door_dir:
            continue

        if furniture_facing_dir:
            if furniture_facing_dir == door_dir or furniture_facing_dir == DIRECTION_OPPOSITES.get(door_dir, door_dir):
                return True
        else:
            pos_lower = furniture_pos.lower()
            door_pos_lower = door_pos.lower()
            if any(w in pos_lower for w in WALLS) and any(w in door_pos_lower for w in WALLS):
                if pos_lower != door_pos_lower:
                    return True
    return False


def _is_directly_in_line(furniture_pos: str, doors: list[dict]) -> bool:
    if not doors or not furniture_pos:
        return False
    pos_lower = furniture_pos.lower()

    for door in doors:
        door_pos = door.get("position", "")
        door_pos_lower = door_pos.lower()
        if ("center" in pos_lower or "middle" in pos_lower) and ("north" in door_pos_lower or "south" in door_pos_lower):
            return True
        if "north wall" in pos_lower and "south" in door_pos_lower:
            return True
        if "south wall" in pos_lower and "north" in door_pos_lower:
            return True
        if "east wall" in pos_lower and "west" in door_pos_lower:
            return True
        if "west wall" in pos_lower and "east" in door_pos_lower:
            return True
    return False


def calculate_commanding_position(elements: list[dict], doors: list[dict]) -> tuple[int, list[Issue]]:
    score = 0
    max_score = 25
    issues = []

    if not doors:
        issues.append(Issue(
            issue="No door detected in room",
            zone="Career",
            score_impact=0,
            explanation="Without a visible door, commanding position cannot be properly evaluated.",
        ))
        return 5, issues

    primary_furniture = _get_primary_furniture(elements)
    if not primary_furniture:
        issues.append(Issue(
            issue="No primary furniture (bed/sofa/desk) detected",
            zone="Career",
            score_impact=-10,
            explanation="Primary furniture placement is essential for Feng Shui evaluation.",
        ))
        return 10, issues

    furniture_with_good_position = 0
    for furniture in primary_furniture:
        f_pos = _get_element_position(furniture)
        f_orient = _get_element_orientation(furniture)

        in_direct_line = _is_directly_in_line(f_pos, doors)
        faces_door = _door_in_facing_direction(f_pos, f_orient, doors)

        if in_direct_line:
            issues.append(Issue(
                issue=f"{_get_element_type(furniture).capitalize()} is directly in line with the door",
                zone="Career",
                score_impact=-7,
                explanation="Furniture in direct line with the door creates Sha Qi (negative energy) and disrupts the commanding position.",
            ))
        elif faces_door:
            furniture_with_good_position += 1
        else:
            issues.append(Issue(
                issue=f"{_get_element_type(furniture).capitalize()} does not face the entrance",
                zone="Career",
                score_impact=-5,
                explanation=f"The {_get_element_type(furniture)} should face the door to establish the commanding position.",
            ))

    if len(primary_furniture) == 0:
        score = 5
    elif furniture_with_good_position == len(primary_furniture):
        score = max_score
    elif furniture_with_good_position >= len(primary_furniture) / 2:
        score = int(max_score * 0.7)
    elif furniture_with_good_position > 0:
        score = int(max_score * 0.4)
    else:
        score = int(max_score * 0.2)

    return score, issues


def calculate_bagua_alignment(elements: list[dict]) -> tuple[int, list[Issue]]:
    score = 0
    max_score = 20
    issues = []

    zone_scores = {}
    for zone, keywords in BAGUA_ZONES.items():
        zone_scores[zone] = {"matched": [], "total": 0, "keywords": keywords}

    for el in elements:
        el_type = _get_element_type(el)
        el_pos = _get_element_position(el)

        for zone, keywords in BAGUA_ZONES.items():
            if _position_contains(el_pos, keywords):
                zone_scores[zone]["total"] += 1

                suitable_types = ZONE_FURNITURE.get(zone, [])
                if any(st in el_type for st in suitable_types):
                    zone_scores[zone]["matched"].append(el_type)

    total_matches = 0
    total_needed = 9

    for zone, data in zone_scores.items():
        match_ratio = len(data["matched"]) / max(1, data["total"])
        if data["total"] > 0 and match_ratio > 0:
            total_matches += min(match_ratio, 1.0)
        elif data["total"] == 0:
            total_matches += 0

    score = int((total_matches / 9) * max_score)

    critical_zones_without_furniture = []
    for zone, data in zone_scores.items():
        if data["total"] == 0 and zone in ["wealth", "career", "relationships"]:
            critical_zones_without_furniture.append(zone)

    if critical_zones_without_furniture:
        issues.append(Issue(
            issue=f"Critical Bagua zones empty: {', '.join(critical_zones_without_furniture)}",
            zone="Health",
            score_impact=-5,
            explanation="These important zones lack any furniture, reducing the room's Feng Shui energy balance.",
        ))

    return max(0, score), issues


def calculate_chi_flow(elements: list[dict], doors: list[dict]) -> tuple[int, list[Issue]]:
    score = 0
    max_score = 20
    issues = []

    center_elements = []
    entrance_blocked = False

    for el in elements:
        el_pos = _get_element_position(el)
        el_type = _get_element_type(el)

        if _position_contains(el_pos, ["center", "middle"]):
            center_elements.append(el_type)

        if doors and _position_contains(el_pos, ["entrance", "entry", "doorway", "entryway"]):
            if "rug" in el_type or "plant" in el_type or "chair" in el_type or "table" in el_type:
                entrance_blocked = True

    pathway_clear = len(center_elements) <= 2
    furniture_count = len(elements)
    clutter_ratio = furniture_count / 20.0

    if entrance_blocked:
        issues.append(Issue(
            issue="Entrance pathway is blocked",
            zone="Health",
            score_impact=-5,
            explanation="Items blocking the entrance prevent Chi from flowing freely into the room.",
        ))

    if not pathway_clear:
        issues.append(Issue(
            issue="Central pathway is cluttered",
            zone="Health",
            score_impact=-3,
            explanation="Too many items in the center of the room obstruct the natural chi pathways.",
        ))

    if furniture_count > 15:
        issues.append(Issue(
            issue="Excessive furniture causing congestion",
            zone="Health",
            score_impact=-3,
            explanation="Too much furniture disrupts the smooth flow of energy through the space.",
        ))

    if pathway_clear and not entrance_blocked and furniture_count <= 10:
        score = max_score
    elif pathway_clear and not entrance_blocked:
        score = int(max_score * 0.8)
    elif not entrance_blocked:
        score = int(max_score * 0.5)
    else:
        score = int(max_score * 0.3)

    return max(0, score), issues


def calculate_five_elements(elements: list[dict]) -> tuple[int, list[Issue]]:
    score = 0
    max_score = 15
    issues = []

    detected_elements = {elem: [] for elem in FIVE_ELEMENTS}

    for el in elements:
        el_type = _get_element_type(el)
        for elem_category, type_list in FIVE_ELEMENTS.items():
            if any(t in el_type for t in type_list):
                detected_elements[elem_category].append(el_type)

    present_elements = [e for e, items in detected_elements.items() if len(items) > 0]
    missing_elements = [e for e, items in detected_elements.items() if len(items) == 0]

    element_count = len(present_elements)
    if element_count == 5:
        score = max_score
    elif element_count == 4:
        score = int(max_score * 0.85)
    elif element_count == 3:
        score = int(max_score * 0.65)
    elif element_count == 2:
        score = int(max_score * 0.4)
    else:
        score = int(max_score * 0.2)

    if missing_elements:
        missing_str = ", ".join(missing_elements).capitalize()
        issues.append(Issue(
            issue=f"Missing Five Elements: {missing_str}",
            zone="Health",
            score_impact=-int((5 - element_count) * 2),
            explanation=f"The {missing_str} elements are not present in the room. A balanced mix of all five elements creates harmonious energy.",
        ))

    return max(0, score), issues


def calculate_light_and_air(elements: list[dict], windows: list[dict]) -> tuple[int, list[Issue]]:
    score = 0
    max_score = 10
    issues = []

    if not windows:
        issues.append(Issue(
            issue="No windows detected in room",
            zone="Health",
            score_impact=-5,
            explanation="Natural light and ventilation are essential for positive Chi. Windows are the primary source.",
        ))
        return 3, issues

    window_count = len(windows)
    obstructed_windows = 0

    for el in elements:
        el_type = _get_element_type(el)
        el_pos = _get_element_position(el)
        for window in windows:
            window_pos = window.get("position", "")
            if window_pos and el_pos:
                if _position_contains(el_pos, ["window", "near window"]) and el_type not in ["curtain", "blind"]:
                    if "curtain" in el_type or "blind" in el_type or "plant" in el_type:
                        obstructed_windows += 1

    if obstructed_windows > 0 and obstructed_windows >= window_count:
        issues.append(Issue(
            issue="All windows are obstructed",
            zone="Health",
            score_impact=-4,
            explanation="Blocking windows prevents natural light and fresh air from entering, stagnating Chi.",
        ))

    if window_count >= 2:
        score = max_score
    elif window_count == 1:
        score = int(max_score * 0.7)
    else:
        score = int(max_score * 0.4)

    return max(0, score), issues


def calculate_mirror_placement(elements: list[dict], mirrors: list[dict], beds: list[dict]) -> tuple[int, list[Issue]]:
    score = max_score = 10
    issues = []

    if not mirrors:
        return score, issues

    for mirror in mirrors:
        mirror_pos = mirror.get("position", "").lower()
        mirror_orient = mirror.get("orientation", "").lower()

        for bed in beds:
            bed_pos = bed.get("position", "").lower()

            if "facing" in mirror_orient:
                if any(w in mirror_orient for w in WALLS) and any(w in bed_pos for w in WALLS):
                    if mirror_orient == bed_pos:
                        issues.append(Issue(
                            issue="Mirror directly faces the bed",
                            zone="Relationships",
                            score_impact=-5,
                            explanation="Mirrors facing beds create restlessness and disrupt sleep energy.",
                        ))
                        score -= 5

            if any(w in mirror_pos for w in ["bed", "bedroom"]):
                issues.append(Issue(
                    issue="Mirror is placed on the wall facing the bed",
                    zone="Relationships",
                    score_impact=-3,
                    explanation="A mirror on the wall facing a bed can cause anxiety and sleep disturbances.",
                ))
                score -= 3

        for kw in ["door", "entrance", "entry"]:
            if kw in mirror_pos or kw in mirror_orient:
                issues.append(Issue(
                    issue="Mirror reflects the entrance door",
                    zone="Career",
                    score_impact=-4,
                    explanation="Mirrors that reflect the door deflect incoming Chi and create instability.",
                ))
                score -= 4
                break

    return max(0, score), issues


def calculate_feng_shui_score(
    elements: list[dict],
    dimensions: Optional[Dimensions] = None,
) -> dict:
    doors = _extract_door_info(elements)
    windows = _extract_windows(elements)
    mirrors = _extract_mirrors(elements)
    beds = _extract_beds(elements)

    commanding_score, commanding_issues = calculate_commanding_position(elements, doors)
    bagua_score, bagua_issues = calculate_bagua_alignment(elements)
    chi_score, chi_issues = calculate_chi_flow(elements, doors)
    elements_score, elements_issues = calculate_five_elements(elements)
    light_score, light_issues = calculate_light_and_air(elements, windows)
    mirror_score, mirror_issues = calculate_mirror_placement(elements, mirrors, beds)

    all_issues = commanding_issues + bagua_issues + chi_issues + elements_issues + light_issues + mirror_issues

    chi_flow_status = "flowing"
    if len(chi_issues) >= 2:
        chi_flow_status = "blocked"
    elif len(chi_issues) >= 1 or commanding_score < 15:
        chi_flow_status = "restricted"

    total = commanding_score + bagua_score + chi_score + elements_score + light_score + mirror_score

    return {
        "total": total,
        "breakdown": ScoreBreakdown(
            commanding_position=commanding_score,
            bagua_alignment=bagua_score,
            chi_flow=chi_score,
            five_elements_balance=elements_score,
            light_and_air=light_score,
            mirror_placement=mirror_score,
        ),
        "issues": all_issues,
        "chi_flow": chi_flow_status,
    }