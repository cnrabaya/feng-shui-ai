from pydantic import BaseModel, Field
from typing import Optional, Literal, Any


FENG_SHUI_SCHOOLS = Literal["black_hat", "form", "three_door", "five_elements", "compass"]

DIMENSION_UNITS = Literal["meters", "feet"]


class Dimensions(BaseModel):
    length: float = Field(gt=0, description="Length of the room")
    width: float = Field(gt=0, description="Width of the room")
    unit: DIMENSION_UNITS = "meters"


class Element(BaseModel):
    type: str
    position: str
    orientation: Optional[str] = None
    size: Optional[str] = None


class Issue(BaseModel):
    issue: str
    zone: Optional[str] = None
    score_impact: int
    explanation: str


class Score(BaseModel):
    total: int
    chi_flow: str
    breakdown: dict[str, Any]
    issues: list[Issue]
    overall_assessment: Optional[str] = None
    school_specific: Optional[dict[str, Any]] = None


class DetectedElement(BaseModel):
    id: str
    type: str
    position_relative_to_camera: Optional[str] = None
    wall_association: Optional[str] = None
    partially_visible: bool = False
    confidence: str = "high"


class ArchitecturalFeatures(BaseModel):
    doors: list[str] = []
    windows: list[str] = []
    visible_walls: list[str] = []


class ExtractionResult(BaseModel):
    elements: list[DetectedElement]
    architectural_features: ArchitecturalFeatures


class MultiImageData(BaseModel):
    image: str = Field(description="Base64-encoded image")
    direction: Literal["north", "south", "east", "west", "not_sure"] = "not_sure"


class MergedRoom(BaseModel):
    confirmed_elements: list[DetectedElement]
    unconfirmed_elements: list[DetectedElement]
    spatial_conflicts: list[dict] = Field(default_factory=list)
    architectural_features: ArchitecturalFeatures = Field(default_factory=ArchitecturalFeatures)
    room_grid: Optional["RoomGrid"] = None


class RoomGrid(BaseModel):
    cells: dict[str, str] = Field(
        description="Mapping of 'row,col' -> furniture type or 'empty'. Row 0 is top (north), col 0 is left (west)."
    )
    grid_size: str = "4x4"
    scale_note: str = "Each cell represents approximately 1/4 of the room. 0,0 = top-left (north-west corner)."


class EvaluateRequest(BaseModel):
    image: Optional[str] = Field(default=None, description="Base64-encoded single image")
    images: Optional[list[MultiImageData]] = Field(default=None, description="Multiple images with direction metadata")
    dimensions: Dimensions = Field(description="Room dimensions (required)")
    session_id: Optional[str] = None
    school: FENG_SHUI_SCHOOLS = "black_hat"
    birth_date: Optional[str] = Field(default=None, description="Birth date for Eight Mansions calculation (YYYY-MM-DD)")
    kua_number: Optional[int] = Field(default=None, description="Kua number (1-9) for Eight Mansions", ge=1, le=9)
    building_date: Optional[str] = Field(default=None, description="Building construction date for Flying Star (YYYY-MM-DD)")


class EvaluateResponse(BaseModel):
    session_id: str
    elements: list[dict]
    score: Score
    room_grid: Optional[RoomGrid] = None
    dimensions: Optional[Dimensions] = None


class ScoreRequest(BaseModel):
    session_id: str
    school: FENG_SHUI_SCHOOLS = "black_hat"
    birth_date: Optional[str] = None
    kua_number: Optional[int] = Field(default=None, ge=1, le=9)
    building_date: Optional[str] = None


class ScoreResponse(BaseModel):
    session_id: str
    school: str
    score: Score
    missing_data: Optional[list[str]] = None


class SuggestRequest(BaseModel):
    session_id: str


class Move(BaseModel):
    element: str
    from_position: str
    to_position: str
    reason: str


class Suggestion(BaseModel):
    id: int
    projected_score: int
    moves: list[Move]
    annotated_image: Optional[str] = None


class SuggestResponse(BaseModel):
    suggestions: list[Suggestion]


class AddElementRequest(BaseModel):
    session_id: str
    element: dict


class AddElementResponse(BaseModel):
    updated_score: Score
    delta: int