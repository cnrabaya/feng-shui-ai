from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal


class Dimensions(BaseModel):
    length: float = Field(description="Room length in meters", gt=0)
    width: float = Field(description="Room width in meters", gt=0)
    unit: str = "meters"


class Element(BaseModel):
    type: str
    position: str
    orientation: Optional[str] = None
    size: Optional[str] = None


class Issue(BaseModel):
    issue: str
    zone: str
    score_impact: int
    explanation: str


class ScoreBreakdown(BaseModel):
    commanding_position: int = 0
    bagua_alignment: int = 0
    chi_flow: int = 0
    five_elements_balance: int = 0
    light_and_air: int = 0
    mirror_placement: int = 0


class Score(BaseModel):
    total: int
    breakdown: ScoreBreakdown
    issues: list[Issue]
    chi_flow: str


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
    dimensions: Optional[Dimensions] = Field(default=None, description="Room dimensions (required when providing multiple images)")
    session_id: Optional[str] = None

    @model_validator(mode="after")
    def dimensions_required_for_images(self):
        if self.images and not self.dimensions:
            raise ValueError("dimensions are required when multiple images are provided")
        return self


class EvaluateResponse(BaseModel):
    session_id: str
    elements: list[dict]
    score: Score
    room_grid: Optional[RoomGrid] = None
    dimensions: Optional[Dimensions] = None


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