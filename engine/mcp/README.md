# Malaysia Data Engine MCP

Read-only Streamable HTTP access to the sanitised public NPRA pharmaceutical
sample. It reads the frozen `public_sample/` CSV snapshots, dated deltas, and
health artefact; it never writes data.

Run locally:

```bash
ENGINE_MCP_SOURCE_SHA=$(git rev-parse HEAD) python -m engine.mcp.server
```

The default endpoint is `http://127.0.0.1:8790/engine`. Set `ENGINE_DATA_ROOT`,
`ENGINE_MCP_HOST`, `ENGINE_MCP_PORT`, or `ENGINE_MCP_PATH` to override local
paths and listener settings. `ENGINE_DATA_ROOT` points at `public_sample/` by
default; the server only reads from that directory.

## Tools

Six read-only tools are exposed:

- `search_pharma` — search one NPRA category by its public searchable fields
- `get_npra_record` — return one exact NPRA record by registration number
- `find_recent_changes` — deduplicated changes from the dated delta artefacts
- `get_pharma_health` — the pipeline health document verbatim
- `find_by_manufacturer` — products and related records for a manufacturer name
- `verify_pharma_artifact` — public stub returning a stable verification hint

## Tests

```bash
pytest -q
```

The test suite requires no network access and exercises the server against the
`public_sample/` stub data layer.
