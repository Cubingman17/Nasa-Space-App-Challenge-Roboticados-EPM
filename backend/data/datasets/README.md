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
units. A CSV is associated with its metric by its stable ID, not by a guessed
name in the CSV.

| File | Metric |
| --- | --- |
| `metric_01.csv`–`metric_02.csv` | Active and passive radiation dosimetry |
| `metric_03.csv`–`metric_15.csv` | Blood pressure, cardiac, ocular, bone, and biochemical metrics |
| `metric_16.csv`–`metric_21.csv` | Cabin and microbiological environment metrics |
| `metric_22.csv`–`metric_25.csv` | Sleep, chronobiology, reaction time, and well-being |
| `metric_26.csv`–`metric_32.csv` | SpO2, HRV, temperature, body composition, and balance metrics |

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

To load all 32 files from this directory into SQLite in one database
transaction, run from the `backend` directory:

```bash
python -m services.import_datasets --astronaut-id A
```

The database stores every point in the shared `measurements` table, keyed by
astronaut, metric, and timestamp. It does not create a separate database table
for each CSV.
