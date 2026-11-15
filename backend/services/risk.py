from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from models.tables import Measurement, MetricCatalog
except ModuleNotFoundError:
    from backend.models.tables import Measurement, MetricCatalog


RISK_SEVERITY = {"low": 0, "moderate": 1, "medium": 1, "high": 2, "critical": 3}


def category_risk(db: Session, astronaut_id: str) -> dict:
    """Summarize risk labels supplied by CSV sources; do not infer thresholds."""
    rows = db.execute(
        select(MetricCatalog.category, MetricCatalog.id, Measurement.recorded_at, Measurement.values_json)
        .join(Measurement, Measurement.metric_id == MetricCatalog.id)
        .where(Measurement.astronaut_id == astronaut_id)
        .order_by(Measurement.recorded_at.desc(), Measurement.id.desc())
    ).all()
    latest_by_metric = {}
    for category, metric_id, recorded_at, values in rows:
        latest_by_metric.setdefault(metric_id, (category, recorded_at, values))

    grouped = defaultdict(list)
    for category, recorded_at, values in latest_by_metric.values():
        label = values.get("risk_level")
        if isinstance(label, str) and label.strip().lower() in RISK_SEVERITY:
            grouped[category].append((label.strip().lower(), recorded_at))

    result = {}
    for category in ("radiation", "microgravity", "psychology", "environment"):
        labels = grouped.get(category, [])
        if not labels:
            result[category] = {"status": "no_data", "source": "csv risk_level labels", "metrics_with_risk": 0}
            continue
        worst = max(labels, key=lambda item: RISK_SEVERITY[item[0]])
        result[category] = {
            "status": worst[0],
            "latest_source_timestamp": worst[1],
            "source": "csv risk_level labels",
            "metrics_with_risk": len(labels),
        }
    return result
