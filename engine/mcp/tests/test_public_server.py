"""Tests for the public Engine MCP server against the public_sample stub data."""

from __future__ import annotations

import asyncio
from datetime import date

from engine.mcp import data, server
from scripts.verify_pharma_sigstore_bundle import VERIFICATION_HINT

EXPECTED_TOOLS = {
    "search_pharma",
    "get_npra_record",
    "find_recent_changes",
    "get_pharma_health",
    "find_by_manufacturer",
    "verify_pharma_artifact",
}


def _tools():
    return asyncio.run(server.app.list_tools())


def test_six_tools_registered():
    assert {tool.name for tool in _tools()} == EXPECTED_TOOLS


def test_all_tools_carry_full_read_only_annotations():
    for tool in _tools():
        annotations = tool.annotations
        assert annotations.read_only_hint is True
        assert annotations.destructive_hint is False
        assert annotations.idempotent_hint is True
        assert annotations.open_world_hint is True


def test_every_tool_input_schema_declares_required():
    for tool in _tools():
        schema = tool.to_mcp_tool().input_schema
        assert "required" in schema, f"{tool.name} inputSchema missing 'required'"
        assert isinstance(schema["required"], list)


def test_search_pharma_returns_matches():
    result = server.search_pharma(q="paracetamol")
    assert result["total"] >= 1
    assert result["matches"]
    assert result["matches"][0]["category"] == "products"


def test_get_npra_record_returns_exact_row():
    result = server.get_npra_record(reg_no="MAL19964378X")
    assert result["reg_no"] == "MAL19964378X"
    assert "Paracetamol" in result["product"]


def test_verify_pharma_artifact_returns_stable_stub():
    result = server.verify_pharma_artifact()
    assert result["bundle_ref"] == ""
    assert result["status"] == "stub"
    assert result["verification_hint"] == VERIFICATION_HINT


def test_find_recent_changes_reads_frozen_delta():
    result = data.load_recent_changes(window_days=30, today=date(2026, 9, 2))
    assert result["total"] >= 1
    assert result["changes"]


def test_get_pharma_health_returns_document():
    result = data.load_health()
    assert result["status"] == "ok"
    assert result["pipeline"] == "npra-pharma"
