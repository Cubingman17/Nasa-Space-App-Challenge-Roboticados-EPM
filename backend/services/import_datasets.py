import argparse
from pathlib import Path

try:
    from data.metrics import METRICS_BY_ID
    from database import SessionLocal, init_db
    from services.csv_import import (
        CSVValidationError,
        parse_metric_csv,
        store_metric_records,
    )
except ModuleNotFoundError:
    from backend.data.metrics import METRICS_BY_ID
    from backend.database import SessionLocal, init_db
    from backend.services.csv_import import (
        CSVValidationError,
        parse_metric_csv,
        store_metric_records,
    )


DEFAULT_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "datasets"


def import_directory(directory: Path, source: str = "synthetic_csv") -> int:
    source = source.strip()
    if not source or len(source) > 120:
        raise ValueError("source must contain 1 to 120 characters")

    files_by_metric: dict[int, Path] = {}
    missing = []
    duplicates = []
    for metric_id in METRICS_BY_ID:
        matches = sorted(directory.glob(f"{metric_id:02d}_*.csv"))
        if not matches:
            missing.append(f"{metric_id:02d}_*.csv")
        elif len(matches) > 1:
            duplicates.extend(path.name for path in matches)
        else:
            files_by_metric[metric_id] = matches[0]

    if missing or duplicates:
        problems = []
        if missing:
            problems.append("Missing files: " + ", ".join(missing))
        if duplicates:
            problems.append("Multiple files for metric IDs: " + ", ".join(duplicates))
        raise FileNotFoundError("; ".join(problems))

    # Validate all 32 files before touching measurement rows in the database.
    parsed_records = {
        metric_id: parse_metric_csv(
            path.read_text(encoding="utf-8-sig"),
            METRICS_BY_ID[metric_id]["category"],
            METRICS_BY_ID[metric_id]["dataset_key"],
        )
        for metric_id, path in files_by_metric.items()
    }

    init_db()
    total_records = 0
    with SessionLocal() as db:
        try:
            for metric_id, records in parsed_records.items():
                store_metric_records(
                    db,
                    metric_id=metric_id,
                    records=records,
                    source=source,
                    replace_existing=True,
                )
                total_records += len(records)
            db.commit()
        except Exception:
            db.rollback()
            raise

    return total_records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and import all 32 metric CSV datasets into SQLite."
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=DEFAULT_DIRECTORY,
        help="Directory containing the numbered metric CSV files",
    )
    parser.add_argument(
        "--source",
        default="synthetic_csv",
        help="Provenance label stored with each observation",
    )
    args = parser.parse_args()

    try:
        count = import_directory(args.directory, args.source)
    except (CSVValidationError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Imported {count} records across {len(METRICS_BY_ID)} metric datasets.")


if __name__ == "__main__":
    main()
