from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field

MetricCategory = Literal[
    "radiation",
    "microgravity",
    "psychology",
    "environment"
]

class Metric(BaseModel):
    id: int = Field(ge=1)
    name: str
    dataset_key: str
    category: MetricCategory
    unit: str
    description: str
    thresholds: dict[str, float] | None = None

class MetricDataPoint(BaseModel):
    metric_id: int
    value: float
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class Vitals(BaseModel):
    bpm: float = Field(gt=0, description="Heart rate in beats per minute")
    spo2: float = Field(
        gt=0,
        le=100,
        description="Blood oxygen saturation percentage"
    )
    sleep_hours: float = Field(
        ge=0,
        description="Sleep duration in hours"
    )
    reaction_time_ms: float = Field(
        gt=0,
        description="Reaction time in milliseconds"
    )

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class Profile(BaseModel):
    astronaut_id: str
    name: str
    age: int | None = Field(default=None, ge=0, le=120)
    height_cm: float | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)
    photo_url: str | None = None
    points: int = Field(default=0, ge=0)
    level: int = Field(default=1, ge=1)
    badges: list[str] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)

class AIResponse(BaseModel):
    analysis: str
    recommendations: list[str] = Field(default_factory=list)
