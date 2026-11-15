import argparse
from pathlib import Path

try:
    from data.metrics import METRICS_BY_ID
    from database import SessionLocal, init_db
    from services.csv_import import (
        CSVValidationError,
        parse_metric_csv,
        store_metric_series,
    )
except ModuleNotFoundError:
    from backend.data.metrics import METRICS_BY_ID
    from backend.database import SessionLocal, init_db
    from backend.services.csv_import import (
        CSVValidationError,
        parse_metric_csv,
        store_metric_series,
    )


DEFAULT_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "datasets"


def import_directory(
    directory: Path,
    astronaut_id: str,
    source: str = "synthetic_csv",
) -> int:
    astronaut_id = astronaut_id.strip()
    source = source.strip()
    if not astronaut_id or len(astronaut_id) > 64:
        raise ValueError("astronaut_id must contain 1 to 64 characters")
    if not source or len(source) > 120:
        raise ValueError("source must contain 1 to 120 characters")

    expected_files = {
        metric_id: directory / f"metric_{metric_id:02d}.csv"
        for metric_id in METRICS_BY_ID
    }
    missing = [path.name for path in expected_files.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing metric CSV files: " + ", ".join(missing)
        )

    # Validate every file before changing the database, so a malformed file
    # cannot leave a partially imported 32-metric dataset.
    parsed_series = {
        metric_id: parse_metric_csv(path.read_text(encoding="utf-8-sig"))
        for metric_id, path in expected_files.items()
    }

    init_db()
    total_points = 0
    with SessionLocal() as db:
        try:
            for metric_id, points in parsed_series.items():
                store_metric_series(
                    db,
                    astronaut_id=astronaut_id,
                    metric_id=metric_id,
                    points=points,
                    source=source,
                    replace_existing=True,
                )
                total_points += len(points)
            db.commit()
        except Exception:
            db.rollback()
            raise

    return total_points


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and import one CSV per metric into SQLite."
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=DEFAULT_DIRECTORY,
        help="Directory containing metric_01.csv through metric_32.csv",
    )
    parser.add_argument(
        "--astronaut-id",
        required=True,
        help="Identifier shared by the imported time series",
    )
    parser.add_argument(
        "--source",
        default="synthetic_csv",
        help="Provenance label stored with each observation",
    )
    args = parser.parse_args()

    try:
        count = import_directory(args.directory, args.astronaut_id, args.source)
    except (CSVValidationError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Imported {count} observations for {len(METRICS_BY_ID)} metrics.")


if __name__ == "__main__":
    main()
