# Week 1 checklist

## Accounts and safety (day 1)
- [ ] GitHub repo created (public), this skeleton pushed
- [ ] Databricks Free Edition account created
- [ ] AWS account created; AWS Budgets alert set (e.g. $5)
- [ ] Anthropic console account created; monthly spend limit set (needed in week 13)

## Local setup
- [ ] `python -m venv .venv && source .venv/bin/activate`
- [ ] `pip install -r requirements.txt`
- [ ] `cp .env.example .env`
- [ ] `pytest -q` passes and `ruff check .` is clean

## First ingestion
- [ ] `python -m src.ingest.transitview` saves one file under data/raw/transitview/
- [ ] Open the JSON. In docs/notes.md write down the top-level keys, the fields per
      vehicle, and anything odd (nulls, duplicate vehicles, timestamps, string vs
      number types). Confirm the response shape matches what you expect; the
      endpoint's format is not guaranteed
- [ ] Run it 5 times a few minutes apart. Do the vehicle records change? How fast?
- [ ] Find the GTFS static URL in SEPTA's GTFS repo releases, set GTFS_URL, run
      `python -m src.ingest.gtfs_static`

## Write-up (15 min)
- [ ] README: project goal, architecture sketch, how to run
- [ ] docs/notes.md: what you learned about the data, what surprised you

## Definition of done
A repo with passing CI, a script that saves raw TransitView snapshots, and
written notes on the shape and quality of the data.
