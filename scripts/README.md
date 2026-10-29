# scripts/

Runnable helpers. Every script that creates data in `data/interim/` or
`data/processed/` must be recorded in `DATASETS.md` when it is used, so
processed data stays traceable to raw data.

- `check_datasets.py` — report which datasets have arrived in `data/raw/`
  (no changes, just a status report). Run it after every download.
