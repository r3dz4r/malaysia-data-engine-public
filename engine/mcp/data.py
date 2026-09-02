"""Read-only access to the sanitised public NPRA sample data."""

from __future__ import annotations

import csv
import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

DATA_ROOT = Path(os.getenv("ENGINE_DATA_ROOT", "public_sample")).expanduser()
CATEGORIES = ("products", "cancelled", "manufacturers", "importers", "wholesalers")
ID_FIELDS = {
    "products": "reg_no",
    "cancelled": "reg_no",
    "manufacturers": "license_no",
    "importers": "license_no",
    "wholesalers": "company",
}
SEARCH_FIELDS = {
    "products": ("product", "manufacturer", "holder", "reg_no"),
    "cancelled": ("product", "manufacturer", "holder", "reg_no"),
    "manufacturers": ("company", "state", "license_no"),
    "importers": ("company", "state", "license_no"),
    "wholesalers": ("company", "state"),
}


def _csv_path(category: str) -> Path:
    if category not in CATEGORIES:
        raise ValueError(f"unknown category: {category}")
    return DATA_ROOT / f"{category}.csv"


def load_csv(category: str) -> list[dict[str, str]]:
    path = _csv_path(category)
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def record_id(category: str, record: dict[str, str] | dict[str, Any]) -> str:
    return str(record.get(ID_FIELDS[category], record.get("id", "")))


def search(category: str, query: str, limit: int) -> dict[str, Any]:
    query_folded = query.casefold()
    matches: list[dict[str, Any]] = []
    for row in load_csv(category):
        values = (row.get(field, "") for field in SEARCH_FIELDS[category])
        if any(query_folded in str(value).casefold() for value in values):
            name = row.get("product") or row.get("company") or row.get("manufacturer") or ""
            snippet = " | ".join(
                value
                for value in (name, row.get("manufacturer"), row.get("holder"), row.get("state"))
                if value
            )
            matches.append(
                {
                    "reg_no": record_id(category, row),
                    "name": name,
                    "category": category,
                    "snippet": snippet,
                }
            )
    return {"matches": matches[:limit], "total": len(matches), "truncated": len(matches) > limit}


def get_record(reg_no: str, category: str | None = None) -> dict[str, str] | None:
    categories = (category,) if category else CATEGORIES
    for item in categories:
        for row in load_csv(item):
            if record_id(item, row) == reg_no:
                return row
    return None


def _change_summary(change_type: str, value: dict[str, Any]) -> str:
    if change_type == "field_changed":
        return f"{value.get('field', 'field')} changed"
    if change_type == "status_changed":
        return f"status changed from {value.get('from', '')} to {value.get('to', '')}".strip()
    return change_type


def load_recent_changes(
    window_days: int, category: str | None = None, *, today: date | None = None
) -> dict[str, Any]:
    if not 1 <= window_days <= 30:
        raise ValueError("window_days must be between 1 and 30")
    end = today or date.today()
    start = end - timedelta(days=window_days)
    changes: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    deltas_dir = DATA_ROOT / "deltas"
    if not deltas_dir.is_dir():
        return {
            "changes": [],
            "window_start": start.isoformat(),
            "window_end": end.isoformat(),
            "total": 0,
        }
    for path in sorted(deltas_dir.glob("*.json"), reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            change_date = date.fromisoformat(str(payload.get("run_date", path.stem)))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if not start < change_date <= end:
            continue
        for source, source_changes in payload.get("sources", {}).items():
            if source not in CATEGORIES or (category and source != category):
                continue
            for change_type in ("new", "removed", "field_changed", "status_changed"):
                for value in source_changes.get(change_type, []):
                    if not isinstance(value, dict):
                        continue
                    identifier = str(
                        value.get("reg_no")
                        or value.get("license_no")
                        or value.get("id")
                        or value.get("company")
                        or ""
                    )
                    key = (source, identifier, change_type)
                    if not identifier or key in seen:
                        continue
                    seen.add(key)
                    changes.append(
                        {
                            "change_date": change_date.isoformat(),
                            "category": source,
                            "reg_no": identifier,
                            "change_type": change_type,
                            "summary": _change_summary(change_type, value),
                        }
                    )
    changes.sort(
        key=lambda item: (item["change_date"], item["category"], item["reg_no"]), reverse=True
    )
    return {
        "changes": changes,
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "total": len(changes),
    }


def load_health() -> dict[str, Any]:
    with (DATA_ROOT / "health.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def find_manufacturer(name: str) -> dict[str, Any]:
    query = name.casefold()
    products = [row for row in load_csv("products") if query in row.get("manufacturer", "").casefold()]
    cancelled = [
        row for row in load_csv("cancelled") if query in row.get("manufacturer", "").casefold()
    ]
    manufacturers = [
        row for row in load_csv("manufacturers") if query in row.get("company", "").casefold()
    ]
    importers = [row for row in load_csv("importers") if query in row.get("company", "").casefold()]
    wholesalers = [
        row for row in load_csv("wholesalers") if query in row.get("company", "").casefold()
    ]

    product_rows = [
        {
            "reg_no": record_id("products", row),
            "product": row.get("product", ""),
            "status": row.get("status", ""),
        }
        for row in products
    ] + [
        {
            "reg_no": record_id("cancelled", row),
            "product": row.get("product", ""),
            "status": row.get("status", ""),
        }
        for row in cancelled
    ]
    related_records = {
        "cancelled": cancelled,
        "manufacturers": manufacturers,
        "importers": importers,
        "wholesalers": wholesalers,
    }
    matches = []
    for row in manufacturers:
        matches.append(
            {
                "name": row.get("company", ""),
                "country": row.get("country", ""),
                "type": "manufacturer",
                "products": product_rows,
                "related_records": related_records,
            }
        )
    for row in importers:
        matches.append(
            {
                "name": row.get("company", ""),
                "country": row.get("country", ""),
                "type": "importer",
                "products": product_rows,
                "related_records": related_records,
            }
        )
    if not matches and (product_rows or wholesalers):
        matches.append(
            {
                "name": name,
                "country": "",
                "type": "manufacturer",
                "products": product_rows,
                "related_records": related_records,
            }
        )
    return {"manufacturer_matches": matches, "total_products": len(product_rows)}
