---
type: Source Map
title: Repository source map and change entry points
description: Practical map from common engineering changes to the repository files, concepts, and verification paths they affect.
tags: [source-map, navigation, engineering]
---

# Repository source map and change entry points

Use this map to locate the authoritative implementation for a change. It intentionally points to conceptual pages rather than duplicating their behavior.

| Concern | Primary files | Start with | Follow-on checks |
| --- | --- | --- | --- |
| Shared records and run orchestration | `scrapers/base.py`, `scrapers/__init__.py` | [Architecture overview](architecture/overview.md) | Both concrete scrapers and stage-level tests |
| ePerolehan listing/detail acquisition | `scrapers/procurement.py`, `scrapers/camofox_client.py` | [Ingestion workflows](workflows/ingestion.md) | Listing/detail fixtures, lifecycle/retry tests, optionally network E2E |
| data.gov.my acquisition/paging | `scrapers/data_gov_my.py` | [Ingestion workflows](workflows/ingestion.md) | Fuel-price fixture/pagination tests, optionally network E2E |
| Vertical validation contracts | `schemas/procurement.yaml`, `schemas/open_dataset.yaml` | [Data model](domain/data-model.md) | Normalization and persistence tests |
| Source status, licence, and risk | `sources.yaml` | [Sources and governance](domain/sources-and-governance.md) | Catalogue tests; reassess privacy/licence before enabling a source |
| Shared persistence and audit tables | `sql/schema.sql` | [Data model](domain/data-model.md) | Both sources’ store/idempotency tests and source-table setup |
| Developer commands and infrastructure | `Makefile`, `docker-compose.yml`, `.env.example` | [Operations runbook](operations/runbook.md) | Port consistency and destructive-command review |
| Test configuration and fixtures | `pyproject.toml`, `tests/`, `tests/fixtures/` | [Testing guide](testing/guide.md) | Select offline, database, or network layer intentionally |
| Documentation automation | `.github/workflows/openwiki-update.yml`, `openwiki/INSTRUCTIONS.md` | [Operations runbook](operations/runbook.md) | Confirm it only updates docs and creates a PR |

## Files that need extra caution

- `scrapers/procurement.py` mixes active Camofox logic with older unimplemented helper stubs and introductory scaffold comments. Follow the tested `fetch`, `extract`, `normalize`, `store`, and audit override paths; do not mistake unused helpers for current behavior.
- `README.md` provides product rationale and a project checklist, but its earlier “scaffold only” statement is stale relative to the active scraper code and recent history. Prefer inspected implementation for runtime claims.
- `Makefile` records intended developer experience, not necessarily existing runner behavior. Its scrape recipes point to a missing Python module command.
- `sql/schema.sql` is idempotent DDL but does not seed source rows. Changes to source entries must account for the `source` table separately.

## Recommended reading order by task

- **New source vertical:** [sources and governance](domain/sources-and-governance.md) → [data model](domain/data-model.md) → [architecture](architecture/overview.md) → [testing](operations/testing.md) → relevant workflow.
- **Active scraper regression:** [ingestion workflows](workflows/ingestion.md) → relevant fixture tests → [operations runbook](operations/runbook.md) for external dependencies.
- **Database/dedup change:** [data model](domain/data-model.md) → `sql/schema.sql` → store/idempotency tests for both sources.
- **Local environment issue:** [operations runbook](operations/runbook.md) → Compose/Makefile/configuration anchors above.
