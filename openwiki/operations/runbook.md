---
type: Operations Runbook
title: Local development and ingestion operations
description: Practical setup, PostgreSQL lifecycle, configuration, documentation automation, and known blockers for running this repository.
tags: [operations, runbook, docker, configuration]
---

# Local development and ingestion operations

## Intended local setup

The project targets Python 3.11+ and uses `uv` to create `.venv` and install `.[dev]`. `make setup` creates the environment and copies `.env.example` only if `.env` does not exist. Do not commit or inspect a live `.env`; use the sample only to identify configuration names.

The documented sequence is:

```bash
make setup
make db-up
make migrate
make test
make lint
```

`make db-up` starts Compose services `postgres` and `adminer`; `make migrate` applies `sql/schema.sql` using `psql`. The [architecture overview](../architecture/overview.md) explains how that schema supports both active scrapers.

## Database connection caveat

Compose exposes PostgreSQL as **host port `54329`** mapped to container port `5432`, and Adminer as `8080`. However, Makefile defaults and `.env.example` specify port `5432`; the provided database/E2E tests also expect `54329`. Override the database port/URL consistently when using Compose, for example:

```bash
make migrate DB_PORT=54329
```

This is a current repository inconsistency, not a claim that either port is universally correct. Verify the target before running migrations or E2E tests.

Compose does not provision Camofox, an application worker, a scheduler, or the source-table bootstrap. Camofox is an external requirement of the [ePerolehan workflow](../workflows/ingestion.md).

## Configuration surface

| Configuration | Used by | Notes |
| --- | --- | --- |
| `DATABASE_URL` | Active scraper storage and audit hooks | Required for database-backed operations; code adapts `postgresql://` to the psycopg SQLAlchemy dialect. |
| `sources.yaml` | Source configuration and policy | Canonical non-secret source inventory. It is read by `load_sources()`, but no inspected code imports it into the `source` SQL table. |
| Camofox base URL/user ID | `ProcurementScraper.fetch()` | Currently hard-coded in `scrapers/procurement.py`; not represented in sample configuration or Compose. |
| Optional sample API/logging variables | `.env.example` only | Sample comments name OpenAI/Codex, Firecrawl, and Hermes monitor variables, but the two active scraper flows do not use them. |

## Intended scrape commands: current blocker

`make seed` and `make scrape` invoke:

```bash
python -m scrapers run --source <id> --dry-run
python -m scrapers run --all --dry-run
```

No `scrapers/__main__.py`, CLI parser, or registered command runner was found. `pyproject.toml` also labels the console entry point as TODO. Consequently, do not present these Make targets as runnable until a CLI is implemented. The underlying classes can still be tested directly, as documented in the [testing guide](testing.md).

The Makefile’s `scrape` comment also conflicts with its recipe/history narrative about which `scraper_status` values should run. Treat source selection as undefined until the runner exists.

## Database bootstrap blocker

`entity_record` and `scrape_run` reference `source(id)`. `sql/schema.sql` creates the table but only shows commented illustrative `INSERT` statements. Before non-dry-run stores can work, an operator must ensure matching source rows exist. The durable fix should be an explicit, idempotent importer/reconciliation command from `sources.yaml`; do not solve it ad hoc inside every scraper. See the [data model](../domain/data-model.md).

## Test and maintenance commands

| Command | Purpose | Preconditions / caution |
| --- | --- | --- |
| `make test` | Run Pytest | Virtual environment needed; database/network tests may need services. |
| `make lint` | Run Ruff lint and formatting check | Virtual environment needed. |
| `make format` | Apply Ruff fixes/formatting | Modifies source; review changes. |
| `make db-down` | Stop Compose services while retaining volume | Does not remove data. |
| `make db-reset` | Recreate DB volume and start services | Destructive to local DB volume. |
| `make clean` | Remove environment, generated data, caches | Destructive to local generated artifacts. |

## Documentation automation

`.github/workflows/openwiki-update.yml` runs on manual dispatch and daily at 08:00 UTC. It installs OpenWiki, runs `openwiki code --update --print`, then opens a PR containing `openwiki`, agent-instruction files, and the workflow itself. It does **not** run migrations, scrapers, or tests.

## Operational checks before a live ingestion

1. Confirm source licence and `pdpa_risk` in `sources.yaml`; a low risk does not replace licence review.
2. Bring up PostgreSQL and apply schema using the actual exposed port.
3. Confirm `source` contains the IDs to be ingested.
4. For ePerolehan, confirm access to the external Camofox endpoint and recheck portal accessibility references.
5. Run offline parser/normalization tests first, then targeted database tests, then explicitly marked `network` E2E tests.
6. Inspect `scrape_run` counters/status after a non-dry run.
