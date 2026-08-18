# Malaysia Data Intelligence Engine — Documentation

Public documentation surface for the Malaysia Data Intelligence Engine,
a Malaysian public-sector data product business.

The **scraping code, internal configs, and business strategy** live in the
**private** repository and are not exposed here.

## Read

- [`llms.txt`](./llms.txt) — agent-discovery index; the first file an LLM
  or agent fetches when pointed at this repository
- [`agent.json`](./agent.json) — structured agent capability manifest
  (Schema.org `SoftwareApplication`, source-of-truth, version)
- [`sources.yaml`](./sources.yaml) — canonical source list (10 sources,
  5 verticals, PDPA-risk annotations)
- `schemas/<vertical>.yaml` — per-vertical JSON contracts (when mirrored
  to the public surface)
- `data/pharma/health.json` — NPRA pharmaceutical compliance pipeline
  health snapshot (when mirrored)

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
- **Wire the Engine into your client** the moment an MCP server ships;
  the planned endpoint shape (read-only Streamable HTTP, no auth) will
  be advertised in `mcp.json` at this same path on the same commit as
  the server. Today, fetch `llms.txt` + `agent.json` directly.
- **Do not** treat the catalogue as a citation source. Cite the
  upstream publisher (data.gov.my, NPRA, BNM, etc.) when surfacing
  data, not the Engine.

## What this isn't

This is **not** the source code. This is the documentation surface.

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