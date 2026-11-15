from fastapi import APIRouter, HTTPException

from backend.data.metrics import METRICS
from backend.models.schemas import Metric

router = APIRouter(prefix="/api/data", tags=["data"])

Category = str

CATEGORIES = {
    "radiation": {
        "name": "Radiation",
        "description": "Radiation exposure and biological response.",
    },
    "microgravity": {
        "name": "Microgravity",
        "description": "Physiological measurements related to microgravity.",
    },
    "psychology": {
        "name": "Psychology",
        "description": "Sleep, alertness, reaction time, and well-being.",
    },
    "environment": {
        "name": "Environment",
        "description": "Spacecraft environmental and microbial measurements.",
    },
}


def _metrics_for(category: str) -> list[Metric]:
    return [Metric(**item) for item in METRICS if item["category"] == category]


@router.get("")
def list_categories() -> dict:
    """Return the metric catalog without inventing observations or risk levels."""
    return {
        "categories": [
            {
                "id": category,
                **details,
                "risk": None,
                "status": "no_data",
                "metrics": _metrics_for(category),
            }
            for category, details in CATEGORIES.items()
        ]
    }


@router.get("/{category}")
def get_category(category: Category) -> dict:
    """Return one category's metric definitions and honest data availability."""
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    return {
        "id": category,
        **CATEGORIES[category],
        "risk": None,
        "status": "no_data",
        "metrics": _metrics_for(category),
        "observations": [],
    }
