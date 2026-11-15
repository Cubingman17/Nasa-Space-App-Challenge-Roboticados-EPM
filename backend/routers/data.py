from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

try:
    from data.metrics import METRICS_BY_CATEGORY, METRICS_BY_ID
    from database import get_db
    from models.schemas import Metric
    from models.tables import Measurement
    from services.csv_import import (
        CSVValidationError,
        SeriesConflictError,
        parse_metric_csv,
        store_metric_records,
    )
except ModuleNotFoundError:
    from backend.data.metrics import METRICS_BY_CATEGORY, METRICS_BY_ID
    from backend.database import get_db
    from backend.models.schemas import Metric
    from backend.models.tables import Measurement
    from backend.services.csv_import import (
        CSVValidationError,
        SeriesConflictError,
        parse_metric_csv,
        store_metric_records,
    )

router = APIRouter(prefix="/api/data", tags=["data"])

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
if set(METRICS_BY_CATEGORY) != set(CATEGORIES):
    raise ValueError("Category descriptions must match categories in metrics.py")


def _metric_model(definition: dict) -> Metric:
    return Metric(**definition)


def _utc_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _observation_counts(db: Session) -> dict[int, int]:
    rows = db.execute(
        select(Measurement.metric_id, func.count(Measurement.id))
        .group_by(Measurement.metric_id)
    ).all()
    return {metric_id: count for metric_id, count in rows}


@router.get("")
def list_categories(db: Session = Depends(get_db)) -> dict:
    """List the four categories and actual imported records per metric."""
    counts = _observation_counts(db)
    categories = []

    for category_id, details in CATEGORIES.items():
        metrics = [
            _metric_model(item).model_dump()
            | {"observation_count": counts.get(item["id"], 0)}
            for item in METRICS_BY_CATEGORY.get(category_id, [])
        ]
        observation_count = sum(metric["observation_count"] for metric in metrics)
        categories.append({
            "id": category_id,
            **details,
            "status": "available" if observation_count else "no_data",
            "observation_count": observation_count,
            "metrics": metrics,
        })

    return {"categories": categories}


@router.get("/{category}")
def get_category(category: str, db: Session = Depends(get_db)) -> dict:
    """Return every CSV-backed metric belonging to one of the four categories."""
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    counts = _observation_counts(db)
    metrics = [
        _metric_model(item).model_dump()
        | {"observation_count": counts.get(item["id"], 0)}
        for item in METRICS_BY_CATEGORY.get(category, [])
    ]
    observation_count = sum(metric["observation_count"] for metric in metrics)
    return {
        "id": category,
        **CATEGORIES[category],
        "status": "available" if observation_count else "no_data",
        "observation_count": observation_count,
        "metrics": metrics,
    }


@router.get("/metrics/{metric_id}/observations")
def get_metric_observations(
    metric_id: int,
    astronaut_id: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=10_000, ge=1, le=100_000),
    db: Session = Depends(get_db),
) -> dict:
    """Return source rows plus one graphable series for each numeric CSV column."""
    definition = METRICS_BY_ID.get(metric_id)
    if definition is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    if start:
        start = _utc_timestamp(start)
    if end:
        end = _utc_timestamp(end)
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="start must be before end")

    statement = select(Measurement).where(Measurement.metric_id == metric_id)
    if astronaut_id:
        statement = statement.where(Measurement.astronaut_id == astronaut_id)
    if start:
        statement = statement.where(Measurement.recorded_at >= start)
    if end:
        statement = statement.where(Measurement.recorded_at <= end)

    rows = db.scalars(
        statement.order_by(Measurement.recorded_at, Measurement.record_id).limit(limit)
    ).all()
    series_points: dict[str, list[dict]] = defaultdict(list)
    observations = []
    for row in rows:
        timestamp = _utc_timestamp(row.recorded_at)
        observations.append({
            "measurement_id": row.record_id,
            "astronaut_id": row.astronaut_id,
            "timestamp": timestamp,
            "values": row.values_json,
        })
        for key, value in row.values_json.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                series_points[key].append({"timestamp": timestamp, "value": value})

    return {
        "metric": _metric_model(definition),
        "astronaut_id": astronaut_id,
        "status": "available" if rows else "no_data",
        "observations": observations,
        "series": [
            {"key": key, "points": points}
            for key, points in sorted(series_points.items())
        ],
    }


@router.post("/metrics/{metric_id}/csv", status_code=201)
async def import_metric_csv(
    metric_id: int,
    request: Request,
    source: str = Query(default="synthetic_csv", min_length=1, max_length=120),
    replace_existing: bool = True,
    db: Session = Depends(get_db),
) -> dict:
    """Validate and import one wide-format source CSV for a metric ID."""
    definition = METRICS_BY_ID.get(metric_id)
    if definition is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    source = source.strip()
    if not source:
        raise HTTPException(status_code=422, detail="source cannot be blank")

    try:
        csv_text = (await request.body()).decode("utf-8-sig")
        records = parse_metric_csv(
            csv_text,
            expected_category=definition["category"],
            expected_metric_key=definition["dataset_key"],
        )
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=422,
            detail="CSV must be encoded as UTF-8",
        ) from error
    except CSVValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    try:
        replaced_count = store_metric_records(
            db,
            metric_id=metric_id,
            records=records,
            source=source,
            replace_existing=replace_existing,
        )
        db.commit()
    except SeriesConflictError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(error)) from error
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not import the CSV because a duplicate record exists",
        ) from error

    return {
        "metric": _metric_model(definition),
        "record_count": len(records),
        "replaced_count": replaced_count,
        "astronaut_ids": sorted({record["astronaut_id"] for record in records}),
        "source": source,
    }
