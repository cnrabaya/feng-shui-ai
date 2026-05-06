from pydantic import BaseModel, Field
from typing import Optional


class Dimensions(BaseModel):
    length: float
    width: float
    height: float
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
    doors: list[dict] = []
    windows: list[dict] = []
    visible_walls: list[str] = []


class ExtractionResult(BaseModel):
    elements: list[DetectedElement]
    architectural_features: ArchitecturalFeatures


class EvaluateRequest(BaseModel):
    image: str = Field(description="Base64-encoded image")
    dimensions: Optional[Dimensions] = None
    session_id: Optional[str] = None


class EvaluateResponse(BaseModel):
    session_id: str
    elements: list[dict]
    score: Score


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