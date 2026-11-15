from datetime import timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from models.tables import HealthAssessment, Measurement, MetricCatalog
except ModuleNotFoundError:
    from backend.models.tables import HealthAssessment, Measurement, MetricCatalog


VITAL_FIELDS = {
    6: ("heart_rate_bpm", "bpm"),
    22: ("sleep_duration_h", "sleep_hours"),
    24: ("mean_reaction_time_ms", "reaction_time_ms"),
    26: ("spo2_percent", "spo2_pct"),
}


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def latest_assessment(db: Session, astronaut_id: str) -> dict | None:
    row = db.scalar(
        select(HealthAssessment)
        .where(HealthAssessment.astronaut_id == astronaut_id)
        .order_by(HealthAssessment.recorded_at.desc(), HealthAssessment.id.desc())
        .limit(1)
    )
    if row is None:
        return None
    return {
        "id": row.id,
        "timestamp": _as_utc(row.recorded_at),
        "overall_status": row.overall_status,
        "metrics": row.metrics_json,
        "input": row.input_json,
        "ai_response": row.ai_response,
    }


def latest_csv_vitals(db: Session, astronaut_id: str) -> dict:
    result = {}
    for metric_id, (field, output_key) in VITAL_FIELDS.items():
        row = db.scalar(
            select(Measurement)
            .where(
                Measurement.astronaut_id == astronaut_id,
                Measurement.metric_id == metric_id,
            )
            .order_by(Measurement.recorded_at.desc(), Measurement.id.desc())
            .limit(1)
        )
        if row is not None:
            result[output_key] = {
                "value": row.values_json.get(field),
                "timestamp": _as_utc(row.recorded_at),
                "source": row.source,
                "measurement_id": row.record_id,
            }
    return result


def astronaut_ids_with_data(db: Session) -> list[str]:
    ids = db.scalars(select(Measurement.astronaut_id).distinct().order_by(Measurement.astronaut_id)).all()
    return list(ids)


def data_summary(db: Session, astronaut_id: str) -> dict:
    rows = db.execute(
        select(MetricCatalog.id, MetricCatalog.name, MetricCatalog.category, Measurement.id)
        .outerjoin(
            Measurement,
            (Measurement.metric_id == MetricCatalog.id)
            & (Measurement.astronaut_id == astronaut_id),
        )
        .order_by(MetricCatalog.id)
    ).all()
    counts: dict[str, int] = {}
    for _metric_id, _name, category, measurement_id in rows:
        counts[category] = counts.get(category, 0) + (1 if measurement_id is not None else 0)
    return {"total_observations": sum(counts.values()), "observations_by_category": counts}
