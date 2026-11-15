import csv
import io
import math
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

try:
    from models.tables import Astronaut, Measurement
except ModuleNotFoundError:
    from backend.models.tables import Astronaut, Measurement


MAX_ROWS_PER_FILE = 100_000
REQUIRED_COLUMNS = {
    "measurement_id",
    "date",
    "astronaut_id",
    "category",
    "metric",
}


class CSVValidationError(ValueError):
    pass


class SeriesConflictError(ValueError):
    pass


def _parse_timestamp(value: str, row_number: int) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise CSVValidationError(
            f"Row {row_number} has an invalid ISO 8601 date"
        ) from error
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)


def _parse_cell(value: str | None, row_number: int, column: str) -> object:
    if value is None or not value.strip():
        return None
    text = value.strip()
    try:
        number = float(text)
    except ValueError:
        return text
    if not math.isfinite(number):
        raise CSVValidationError(
            f"Row {row_number}, column {column!r} has a non-finite number"
        )
    if number.is_integer():
        return int(number)
    return number


def parse_metric_csv(
    content: str,
    expected_category: str,
    expected_metric_key: str,
) -> list[dict]:
    """Parse one of the supplied wide-format CSV files without dropping fields."""
    if not content.strip():
        raise CSVValidationError("CSV is empty")

    reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")))
    if not reader.fieldnames:
        raise CSVValidationError("CSV must have a header row")

    normalized_headers = [
        header.strip().lower() if header else ""
        for header in reader.fieldnames
    ]
    if any(not header for header in normalized_headers):
        raise CSVValidationError("CSV column names cannot be blank")
    if len(set(normalized_headers)) != len(normalized_headers):
        raise CSVValidationError("CSV contains duplicate column names")
    missing = REQUIRED_COLUMNS - set(normalized_headers)
    if missing:
        raise CSVValidationError(
            "CSV is missing required columns: " + ", ".join(sorted(missing))
        )

    columns = dict(zip(normalized_headers, reader.fieldnames))
    variable_columns = [
        (header, columns[header])
        for header in normalized_headers
        if header not in REQUIRED_COLUMNS
    ]
    records: list[dict] = []
    seen_record_ids: set[tuple[str, str]] = set()
    metric_key: str | None = None

    for row_number, row in enumerate(reader, start=2):
        if row_number > MAX_ROWS_PER_FILE + 1:
            raise CSVValidationError(
                f"CSV exceeds the {MAX_ROWS_PER_FILE} row limit"
            )
        if None in row:
            raise CSVValidationError(f"Row {row_number} has too many columns")

        record_id = (row.get(columns["measurement_id"]) or "").strip()
        astronaut_id = (row.get(columns["astronaut_id"]) or "").strip()
        category = (row.get(columns["category"]) or "").strip().lower()
        current_metric_key = (row.get(columns["metric"]) or "").strip()
        if not record_id or not astronaut_id or not current_metric_key:
            raise CSVValidationError(
                f"Row {row_number} needs measurement_id, astronaut_id, and metric"
            )
        if len(record_id) > 120 or len(astronaut_id) > 64:
            raise CSVValidationError(
                f"Row {row_number} has an ID longer than the supported limit"
            )
        if category != expected_category:
            raise CSVValidationError(
                f"Row {row_number} category {category!r} does not match "
                f"catalog category {expected_category!r}"
            )
        if current_metric_key != expected_metric_key:
            raise CSVValidationError(
                f"Row {row_number} metric {current_metric_key!r} does not match "
                f"catalog dataset key {expected_metric_key!r}"
            )
        if metric_key is None:
            metric_key = current_metric_key
        elif current_metric_key != metric_key:
            raise CSVValidationError(
                f"Row {row_number} metric does not match the rest of this file"
            )

        record_key = (astronaut_id, record_id)
        if record_key in seen_record_ids:
            raise CSVValidationError(
                f"Duplicate measurement_id {record_id!r} for {astronaut_id!r}"
            )
        seen_record_ids.add(record_key)

        timestamp = _parse_timestamp(
            row.get(columns["date"]) or "",
            row_number,
        )
        values = {
            header: _parse_cell(row.get(original), row_number, header)
            for header, original in variable_columns
        }
        records.append({
            "record_id": record_id,
            "astronaut_id": astronaut_id,
            "recorded_at": timestamp,
            "metric_key": metric_key,
            "values": values,
        })

    if not records:
        raise CSVValidationError("CSV contains no measurement rows")
    records.sort(key=lambda record: (record["astronaut_id"], record["recorded_at"]))
    return records


def store_metric_records(
    db: Session,
    metric_id: int,
    records: list[dict],
    source: str,
    replace_existing: bool = True,
) -> int:
    """Stage one CSV's records in a session; the caller controls commit."""
    existing = db.scalars(
        select(Measurement).where(Measurement.metric_id == metric_id)
    ).all()

    replaced_count = 0
    if replace_existing:
        replaced_count = len(existing)
        db.execute(
            delete(Measurement).where(Measurement.metric_id == metric_id)
        )
    else:
        existing_record_ids = {
            (row.astronaut_id, row.record_id)
            for row in existing
        }
        incoming_record_ids = {
            (record["astronaut_id"], record["record_id"])
            for record in records
        }
        if incoming_record_ids & existing_record_ids:
            raise SeriesConflictError(
                "CSV contains measurement IDs already stored for this metric"
            )

    astronaut_ids = {record["astronaut_id"] for record in records}
    existing_astronaut_ids = set(db.scalars(
        select(Astronaut.id).where(Astronaut.id.in_(astronaut_ids))
    ).all())
    new_astronauts = astronaut_ids - existing_astronaut_ids
    if new_astronauts:
        db.add_all(Astronaut(id=astronaut_id) for astronaut_id in new_astronauts)
        db.flush()

    db.add_all([
        Measurement(
            astronaut_id=record["astronaut_id"],
            metric_id=metric_id,
            record_id=record["record_id"],
            recorded_at=record["recorded_at"],
            values_json=record["values"],
            source=source,
        )
        for record in records
    ])
    return replaced_count
