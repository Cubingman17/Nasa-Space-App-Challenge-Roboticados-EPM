# Astronaut health CSV datasets

This directory contains one source CSV for each of the 32 metric IDs in
`backend/data/metrics.py`. File prefixes map to IDs (`01_...csv` is metric 1,
`32_...csv` is metric 32); the `metric` and `category` columns are validated
against that catalog during import.

## Source row format

The supplied files are wide tables. Each row represents one recorded
observation and contains these shared columns:

```text
measurement_id,date,astronaut_id,category,metric
```

The remaining columns are measurements or source labels specific to that CSV.
For example, active radiation includes dose rate, cumulative dose, particle
flux, and risk level. All fields are retained in the database; finite numeric
fields become graph series, while text labels remain available in the raw
observation. Dates are stored as UTC; timezone-naive dates in the supplied
files are interpreted as UTC.

## Import all 32 files

Run from the `backend` directory:

```bash
python -m services.import_datasets
```

The importer requires exactly one numbered CSV for each ID, validates all
files before changing measurement rows, and then replaces the matching metric
records in one transaction. Imported observations keep their astronaut IDs and
are marked with the source `synthetic_csv`.

## API

- `GET /api/data` lists the four categories and counts for their metrics.
- `GET /api/data/{category}` lists the metrics in one category.
- `GET /api/data/metrics/{id}/observations` returns raw rows and a numeric
  time series for every measurement column. Add `?astronaut_id=AST-001` to
  filter by astronaut.
- `POST /api/data/metrics/{id}/csv` imports one wide CSV; send the CSV bytes as
  the request body.

SQLite uses one normalized `measurements` table keyed by astronaut, metric, and
source record ID. The variable measurement columns are stored as JSON so the
32 CSVs can keep their different schemas without losing fields.
