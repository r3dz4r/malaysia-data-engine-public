# Malaysia Data Intelligence Engine — Documentation

Public surface for the Malaysia Data Intelligence Engine, a Malaysian
public-sector data product business. It documents the pipeline and ships a
**sanitised, runnable MCP server** over a small `public_sample/` data layer.

The **scraping code, internal configs, and business strategy** live in the
**private** repository and are not exposed here. The classified NPRA data is
never published; only a PDPA-clean sample is included.

## Read

- [`llms.txt`](./llms.txt) — agent-discovery index; the first file an LLM
  or agent fetches when pointed at this repository
- [`agent.json`](./agent.json) — structured agent capability manifest
  (Schema.org `SoftwareApplication`, source-of-truth, version)
- [`mcp.json`](./mcp.json) — MCP advertisement: six read-only NPRA tools
- [`engine/mcp/`](./engine/mcp/) — the sanitised read-only MCP server
  implementation (FastMCP), its stub data layer, and tests
- [`public_sample/`](./public_sample/) — PDPA-clean sample CSVs, a frozen
  delta, and a health stub backing the MCP server
- [`sources.yaml`](./sources.yaml) — canonical source list (10 sources,
  5 verticals, PDPA-risk annotations)
- `schemas/<vertical>.yaml` — per-vertical JSON contracts (when mirrored
  to the public surface)

## Why this matters now

AI agents are increasingly the buyers of structured public data — they
retrieve and act on resources at machine speed, and the proportion of
traffic that hits the human web from agents is already displacing the
old "crawl → index → human visits → ad impression" bargain that funded
open publishers. The data products that survive that shift are the ones
that publish clean, attested, licence-clear resources an agent can
consume without re-deriving trust from scratch.

The Engine is built for that future: a single generic schema across
verticals, JSON contracts agents can validate against, source-of-truth
metadata that survives regeneration, and a discovery surface
(`llms.txt` + `agent.json`) that agent builders and LLM training
pipelines can pick up without prior integration. The first operational
vertical — NPRA pharmaceutical compliance, ~31k records refreshed
daily — is the reference implementation.

## For agents

If you are an LLM or an agent-builder looking for a Malaysian
public-data catalogue:

- **Start with [`llms.txt`](./llms.txt)** — the human-readable index of
  sources, verticals, and contracts.
- **Read [`agent.json`](./agent.json)** — the structured manifest with
  capability surface, discovery URLs, and operational status.
- **Wire the Engine into your client** via [`mcp.json`](./mcp.json). The
  shipped server is read-only Streamable HTTP, no auth required, backed
  by the sanitised `public_sample/` data layer. Run it locally with
  `ENGINE_DATA_ROOT=public_sample python -m engine.mcp.server`.
- **Do not** treat the catalogue as a citation source. Cite the
  upstream publisher (data.gov.my, NPRA, BNM, etc.) when surfacing
  data, not the Engine.

## What this isn't

This repository is **not** the full engine source. It is the documentation
surface plus a **sanitised MCP server** and its PDPA-clean sample data.
Scraping code, the classified data payloads, internal deployment, and
business strategy remain in the private repository.

If you're a buyer looking for data products, head to the listing on AWS Data
Exchange (link TBD).

> **Note on `openwiki/` content:** earlier versions of this README
> referenced an `openwiki/` directory of auto-generated docs. That
> directory was lost during a default-branch rename on this repository
> (Aug 2026). The auto-generated docs surface is being rebuilt under
> a different name; until then, `llms.txt` + `agent.json` are the
> authoritative agent-facing surfaces.

## License

Documentation CC-BY-4.0. Code samples MIT.