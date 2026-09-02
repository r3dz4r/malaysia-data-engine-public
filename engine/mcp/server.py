"""Streamable HTTP MCP server exposing read-only NPRA pharma sample records."""

from __future__ import annotations

import os
from typing import Annotated, Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from engine.mcp import data
from scripts.verify_pharma_sigstore_bundle import VERIFICATION_HINT

SOURCE_COMMIT_SHA = os.getenv("ENGINE_MCP_SOURCE_SHA", "unknown")
SOURCE_COMMIT_DATE = os.getenv("ENGINE_MCP_SOURCE_DATE", "unknown")
MCP_HOST = os.getenv("ENGINE_MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("ENGINE_MCP_PORT", "8790"))
MCP_PATH = os.getenv("ENGINE_MCP_PATH", "/engine")

Category = Literal["products", "cancelled", "manufacturers", "importers", "wholesalers"]

READ_ONLY_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True
)

app = FastMCP(
    "malaysia-data-engine-mcp",
    version=SOURCE_COMMIT_SHA,
    instructions=(
        "Read-only NPRA pharmaceutical records backed by the public sample data. "
        "This server never modifies pipeline artefacts."
    ),
)


@app.tool(annotations=READ_ONLY_TOOL_ANNOTATIONS)
def search_pharma(
    q: Annotated[
        str,
        Field(
            min_length=2, max_length=200, description="Case-insensitive substring to search for."
        ),
    ],
    category: Annotated[
        Category,
        Field(description="NPRA category to search. Defaults to products."),
    ] = "products",
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=100,
            description="Maximum number of matching products to return. Default 20.",
        ),
    ] = 20,
) -> dict:
    """Search one NPRA category by its public searchable fields."""
    return data.search(category, q, limit)


@app.tool(annotations=READ_ONLY_TOOL_ANNOTATIONS)
def get_npra_record(
    reg_no: Annotated[
        str,
        Field(
            min_length=1,
            max_length=200,
            description="Exact NPRA registration number to look up (e.g. MAL16100027TCR).",
        ),
    ],
    category: Annotated[
        Category | None,
        Field(
            description=(
                "Filter the lookup to one NPRA category; defaults to searching all categories."
            )
        ),
    ] = None,
) -> dict:
    """Return one exact NPRA record, searching all categories by default."""
    record = data.get_record(reg_no, category)
    return record if record is not None else {"error": "not found", "reg_no": reg_no}


@app.tool(annotations=READ_ONLY_TOOL_ANNOTATIONS)
def find_recent_changes(
    window_days: Annotated[
        int,
        Field(
            ge=1,
            le=30,
            description="Number of days back to include registry changes. Default 7.",
        ),
    ] = 7,
    category: Annotated[
        Category | None,
        Field(description="Filter changes to one category; all categories by default."),
    ] = None,
) -> dict:
    """Return deduplicated changes from the dated pipeline delta artefacts."""
    return data.load_recent_changes(window_days, category)


@app.tool(annotations=READ_ONLY_TOOL_ANNOTATIONS)
def get_pharma_health() -> dict:
    """Return the pipeline-produced pharma health document verbatim."""
    return data.load_health()


@app.tool(annotations=READ_ONLY_TOOL_ANNOTATIONS)
def find_by_manufacturer(
    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=200,
            description="Manufacturer-name substring to search for (case-insensitive).",
        ),
    ]
) -> dict:
    """Find products and related NPRA records for a manufacturer-name substring."""
    return data.find_manufacturer(name)


@app.tool(annotations=READ_ONLY_TOOL_ANNOTATIONS)
def verify_pharma_artifact() -> dict:
    """Return the public verification stub for the signed pharma provenance bundle."""
    return {
        "bundle_ref": "",
        "verification_hint": VERIFICATION_HINT,
        "status": "stub",
    }


for _component in app._local_provider._components.values():  # type: ignore[attr-defined]
    parameters = getattr(_component, "parameters", None)
    if isinstance(parameters, dict):
        parameters.setdefault("required", [])


if __name__ == "__main__":
    app.run(
        transport="http",
        host=MCP_HOST,
        port=MCP_PORT,
        path=MCP_PATH,
        stateless_http=True,
        show_banner=False,
    )
