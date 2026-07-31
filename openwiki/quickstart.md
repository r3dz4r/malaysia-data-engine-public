---
type: Project Guide
title: Malaysia Public Data Intelligence Engine quickstart
description: Entry point for the reusable Malaysian public-data ingestion pipeline, its active sources, architecture, operations, and validation guidance.
tags: [quickstart, data-engineering, malaysia, scraping]
---

# Malaysia Public Data Intelligence Engine

This repository is a Python 3.11+ foundation for harvesting Malaysian public-sector data, normalizing it into source-specific JSON contracts, and storing it in PostgreSQL for later curation and licensed distribution. It is designed around reusable ingestion mechanics rather than a single vertical.

The current code implements two sources: ePerolehan government-procurement notices and the `fuelprice` series from data.gov.my. The source catalogue also records candidate verticals such as property transactions and company registry data; those are not implemented scrapers.

## Start here

1. Read the [architecture overview](architecture/overview.md) to understand the shared `fetch → extract → normalize → store` contract, registry, and database boundary.
2. Read [domain and data model](domain/data-model.md) before changing schemas, record identity, persistence, or deduplication semantics.
3. Read [sources and governance](domain/sources-and-governance.md) before activating a source, handling procurement fields, or making licence and privacy decisions.
4. Read [ingestion workflows](workflows/ingestion.md) before changing either active scraper or its external behavior.
5. Use the [operations runbook](operations/runbook.md) for local setup and known execution blockers.
6. Use the [testing guide](operations/testing.md) to choose the right offline, database, or live-network checks.
7. Use the [source map](source-map.md) when you know the change area and need the authoritative files and checks.

## Current implementation at a glance

| Area | Current state | Source anchors |
| --- | --- | --- |
| Shared pipeline | Abstract `Scraper` orchestrates source-specific stages and counters | `scrapers/base.py` |
| Procurement | Camofox-driven ePerolehan listing parse, five lifecycle tabs, optional detail enrichment | `scrapers/procurement.py`, `scrapers/camofox_client.py` |
| Open data | data.gov.my date-keyed ingestion; handles observed repeated API window behavior | `scrapers/data_gov_my.py` |
| Persistence | PostgreSQL `source`, `entity_record`, and `scrape_run` tables | `sql/schema.sql` |
| Contracts | JSON Schemas for procurement tenders and open-data observations | `schemas/procurement.yaml`, `schemas/open_dataset.yaml` |
| Verification | Pytest fixtures, parser tests, persistence/idempotency checks, and marked live E2E tests | `tests/`, `pyproject.toml` |

## Product and policy boundary

The stated product direction is curated Malaysian public data for licensed resale. `sources.yaml` is the operational catalogue: it records source status, refresh frequency, licence notes, and a `pdpa_risk` level. The shared runner rejects `high`-risk sources, while the procurement schema permits agency/role or generic contact information but explicitly excludes personal names, mobile numbers, and personal email addresses. [Sources and governance](domain/sources-and-governance.md) is canonical for those commercial and privacy boundaries; the [data model](domain/data-model.md) shows how they constrain every [ingestion workflow](workflows/ingestion.md).

## What recent history says

Recent commits supplied for this initialization show a concentrated ePerolehan Phase 2/2.5 progression: listing capture and parsing, schema validation, SQL storage/auditing, idempotency checks, Camofox detail-page enrichment, lifecycle-tab selection, end-to-end coverage, and a final retry/identity stabilization fix. The repository README and catalogue were updated to describe this active state. When touching procurement, preserve the fixture-backed parsing and the retry behavior documented in [ingestion workflows](workflows/ingestion.md), not the older “scaffold” comments that remain in some module headers.

## Important current gaps

Treat these as engineering follow-ups, not undocumented assumptions:

- **Runner is absent:** `Makefile` invokes `python -m scrapers run ...`, but no `scrapers.__main__` or CLI module is present. See [operations runbook](operations/runbook.md).
- **Source-table bootstrap is manual/unclear:** foreign keys require rows in `source`, but `sql/schema.sql` contains only commented example seed SQL. See [domain and data model](domain/data-model.md).
- **Local connectivity mismatch:** Compose exposes Postgres on host port `54329`, while Makefile and sample configuration default to `5432`.
- **Camofox is external:** procurement hard-codes its Camofox service endpoint and Compose does not provision it.
- **Retention/update semantics differ from narrative:** concrete stores write normalized JSON to both `raw` and `normalized`, and identity conflicts are ignored rather than updated.

## Backlog

- **Executable CLI and source selection** — `Makefile:94-103`, `pyproject.toml:51-54`; document after a runner exists because current commands reference missing code.
- **Source bootstrap/import** — `sql/schema.sql:114-120`; document an operator workflow once `sources.yaml` can populate or reconcile `source` rows.
- **Future source verticals** — `sources.yaml:36-170`; property, registry, financial, statistics, health, invoice, weather, and publication entries are catalogued but have no registered implementations.
- **Award-specific procurement fields** — `README.md:147`; deferred because the active implementation targets notices and optional notice-detail enrichment.
