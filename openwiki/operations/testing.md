---
type: Testing Guide
title: Testing and validation strategy
description: Explains the fixture, unit, database, and network test layers for active scrapers and how to validate changes without overstating live coverage.
tags: [testing, pytest, quality, scrapers]
---

# Testing and validation strategy

Tests live under `tests/`; pytest is configured in `pyproject.toml` with strict markers and strict configuration. The suite combines offline parser/schema tests with database-backed and live-network checks. There is no checked-in Python CI workflow, so passing locally is the available repository-level signal unless external automation is added.

## Test layers

| Layer | What it verifies | Key files |
|---|---|---|
| Registry and schema smoke tests | Active-source metadata, schema existence/basic shape | `tests/test_sources_yaml.py`, `tests/test_schemas_exist.py` |
| Offline parser and normalizer tests | Snapshot/API fixture parsing, field shape, JSON Schema validation | `test_procurement_fetch.py`, `test_procurement_detail.py`, `test_procurement_normalize.py`, `test_data_gov_my_extract.py`, `test_data_gov_my_pagination.py` |
| Store tests | First insert versus native-identity conflict behavior | `test_procurement_store.py`, `test_data_gov_my_store.py` |
| Network/E2E tests | Live source interaction, PostgreSQL rows, scrape-run terminal state | `test_procurement_e2e.py`, `test_procurement_enriched_e2e.py`, `test_data_gov_my_e2e.py` |
| Repeat-run idempotency tests | Second run is deduplicated | `test_procurement_idempotent.py`, `test_procurement_enriched_idempotent.py`, `test_data_gov_my_idempotent.py` |

This layering follows the architecture: fixtures test parsing and schema changes before the same normalized records reach `entity_record`; database/E2E tests then verify the identity and audit behavior described in [architecture overview](../architecture/overview.md).

## Fixtures first

The procurement tests use captured Camofox accessibility snapshots in `tests/fixtures/`, including an advertised-listing sample and a tender-detail sample. Test these when changing regexes, lifecycle-tab logic, date parsing, field extraction, retry behavior, or enrichment. The detail fixture validates fields such as tender ID, indicative value, validity period, supplier status, coverage, and `kod_bidang` hierarchy.

The data.gov.my tests use a fuelprice JSON fixture. They explicitly model the upstream broken-offset behavior: a repeated response must not emit duplicate date identities and fetch stops when a window contributes no new IDs. This is a key safety condition for the workflow documented in [ingestion workflows](../workflows/ingestion.md).

## Database and network tests

Network tests are marked `@pytest.mark.network`, but `make test` does not filter them. They assume live endpoints and a database URL that defaults to `postgresql+psycopg://malaysia:malaysia@localhost:54329/malaysia_data`, matching the compose host port rather than the Makefile default. They clean records for their own source/entity type and examine `scrape_run` afterward.

Before running them:

1. Start and migrate local PostgreSQL as described in the [runbook](runbook.md).
2. Ensure matching `source` rows exist, because the schema's foreign keys require them.
3. Confirm Camofox availability for procurement; its base URL is currently hard-coded in `ProcurementScraper.fetch()`.
4. Treat external portal/API changes, fixed browser waits, and live data volatility as possible test failure causes.

`test_procurement_e2e.py` expects no record errors and a run under 180 seconds. Enriched procurement E2E asks for three detail drill-downs. data.gov.my E2E asserts more than 50 inserts on a clean database, so rerunning without cleanup should use its separate idempotency test expectations rather than first-run expectations.

## Change checklist

### Scraper parser or source UI

- Update/add a static fixture that demonstrates the changed source shape.
- Update parsing tests before relying on a network run.
- For ePerolehan, exercise the affected lifecycle tab and detail/no-detail behavior.
- Reassess PII exposure; keep personal-contact fields out of normalized output per [sources and governance](../domain/sources-and-governance.md).

### Schema or normalization

- Change the relevant schema and normalizer together.
- Add a positive validation test and a failure case for an invalid required or formatted field.
- Revisit record identity if the source-native key or identity granularity changes.

### Persistence or audit

- Test first insert, duplicate conflict, hash/envelope values, and scrape-run counters/status.
- Be explicit whether the desired behavior is ignore, update, or versioning: current stores ignore native-key conflicts.
- If raw provenance changes, test the distinction between `raw` and `normalized` explicitly.

### Commands and automation

- Run `make lint` after Python edits.
- Do not mistake the scheduled OpenWiki workflow for test coverage: its scope is documented in the [runbook](runbook.md).
- If adding a CLI or CI, include a focused test that proves the documented command and update the [ingestion workflows](../workflows/ingestion.md) and runbook.
