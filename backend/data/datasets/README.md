# Metric CSV datasets

Keep one UTF-8 CSV file per metric in this directory. Use the stable metric ID
from `backend/data/metrics.py` in each filename: `metric_01.csv` through
`metric_32.csv`.

## Required format

Each file must contain exactly one time series with these required columns:

```csv
timestamp,value
2026-01-01T00:00:00Z,12.5
2026-01-01T01:00:00Z,12.7
```

- `timestamp`: ISO 8601 date/time. Include `Z` or a UTC offset; date-only and
  timezone-naive ISO dates are interpreted as UTC.
- `value`: finite numeric value, expressed in the unit defined for that metric
  in `backend/data/metrics.py`.
- Timestamps must be unique within a file. Rows may be in any order; the
  importer sorts them.
- Keep the metric ID, unit, sampling interval, and value meaning consistent
  throughout each file. Do not add calculated risk labels or fabricated
  astronaut profile fields.

The metric catalog is the source of truth for IDs, categories, names, and
units. A CSV is associated with its metric by the API path, not by its filename
or by a guessed name in the CSV.

## Import and query

Send each file's contents to:

```text
POST /api/data/metrics/{metric_id}/csv?astronaut_id=A
Content-Type: text/csv
```

The importer validates the full file before saving. By default, importing the
same astronaut/metric again replaces that time series, so re-imports do not
duplicate points. To read the series:

```text
GET /api/data/metrics/{metric_id}/observations?astronaut_id=A
```

The database stores every point in the shared `measurements` table, keyed by
astronaut, metric, and timestamp. It does not create a separate database table
for each CSV.
