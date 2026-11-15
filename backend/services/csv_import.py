import csv
import io
import math
from datetime import datetime, timezone


MAX_ROWS_PER_FILE = 100_000


class CSVValidationError(ValueError):
    pass


def parse_metric_csv(content: str) -> list[tuple[datetime, float]]:
    """Parse the canonical timestamp,value CSV format for a single metric."""
    if not content.strip():
        raise CSVValidationError("CSV is empty")

    reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")))
    if not reader.fieldnames:
        raise CSVValidationError("CSV must have a header row")

    normalized_headers = [header.strip().lower() for header in reader.fieldnames]
    if len(set(normalized_headers)) != len(normalized_headers):
        raise CSVValidationError("CSV contains duplicate column names")
    if not {"timestamp", "value"}.issubset(normalized_headers):
        raise CSVValidationError("CSV must contain timestamp and value columns")

    timestamp_column = reader.fieldnames[normalized_headers.index("timestamp")]
    value_column = reader.fieldnames[normalized_headers.index("value")]
    points: list[tuple[datetime, float]] = []
    timestamps: set[datetime] = set()

    for row_number, row in enumerate(reader, start=2):
        if row_number > MAX_ROWS_PER_FILE + 1:
            raise CSVValidationError(
                f"CSV exceeds the {MAX_ROWS_PER_FILE} row limit"
            )
        if None in row:
            raise CSVValidationError(f"Row {row_number} has too many columns")

        raw_timestamp = (row.get(timestamp_column) or "").strip()
        raw_value = (row.get(value_column) or "").strip()
        if not raw_timestamp or not raw_value:
            raise CSVValidationError(
                f"Row {row_number} must have timestamp and value"
            )

        try:
            timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
        except ValueError as error:
            raise CSVValidationError(
                f"Row {row_number} has an invalid ISO 8601 timestamp"
            ) from error
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        timestamp = timestamp.astimezone(timezone.utc)

        try:
            value = float(raw_value)
        except ValueError as error:
            raise CSVValidationError(
                f"Row {row_number} has a non-numeric value"
            ) from error
        if not math.isfinite(value):
            raise CSVValidationError(
                f"Row {row_number} value must be a finite number"
            )
        if timestamp in timestamps:
            raise CSVValidationError(
                f"Timestamp {raw_timestamp!r} appears more than once"
            )

        timestamps.add(timestamp)
        points.append((timestamp, value))

    if not points:
        raise CSVValidationError("CSV contains no measurement rows")

    points.sort(key=lambda point: point[0])
    return points
