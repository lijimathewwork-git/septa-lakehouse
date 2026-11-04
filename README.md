# SEPTA Lakehouse

Real-time transit pipeline (Python, S3, Databricks/Delta, dbt) plus an AI
analyst agent that answers questions over the gold tables.

## Architecture (target)
ingest (Python) -> raw JSON in S3 -> bronze -> silver -> gold (dbt) -> dashboard
                                                             \-> analyst agent

## Status
- [x] Week 1: repo + local ingestion
- [ ] Week 2: scheduled ingestion to S3

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.ingest.transitview
pytest -q
```

## Design decisions
- Ingestion stores raw payloads untouched, wrapped in a metadata envelope.
  Cleaning happens in silver so any run can be replayed.
- Hive-style partitions (dt=/hr=) so Spark can prune by date.

## Data
SEPTA public APIs and GTFS feeds. Check SEPTA's developer page for terms.
