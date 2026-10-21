"""Referential-integrity and schema checks for the crosswalk data."""
from __future__ import annotations

import re

from .model import SECTOR_PRIORITIES, Crosswalk

CONTROL_ID = re.compile(r"^AICC-\d{2,3}$")
REQUIRED_CONTROL_FIELDS = ("id", "title", "category", "objective", "maps", "sectors")


def validate(cw: Crosswalk) -> list[str]:
    """Return a list of human-readable problems. Empty list means valid."""
    errors: list[str] = []

    # Framework items: unique ids within and across frameworks
    seen_items: dict[str, str] = {}
    for fw_id, fw in cw.frameworks.items():
        for key in ("name", "short", "source_url", "items"):
            if not fw.get(key):
                errors.append(f"Framework {fw_id}: missing '{key}'")
        for item in fw.get("items", []):
            iid = item["id"]
            if iid in seen_items:
                errors.append(f"Item id '{iid}' appears in both {seen_items[iid]} and {fw_id}")
            seen_items[iid] = fw_id
            if not item.get("title"):
                errors.append(f"{fw_id}/{iid}: missing title")

    # Controls
    seen_controls: set[str] = set()
    for c in cw.controls:
        cid = c.get("id", "<no id>")
        for key in REQUIRED_CONTROL_FIELDS:
            if not c.get(key):
                errors.append(f"{cid}: missing '{key}'")
        if not CONTROL_ID.match(str(cid)):
            errors.append(f"{cid}: id must look like AICC-01")
        if cid in seen_controls:
            errors.append(f"{cid}: duplicate control id")
        seen_controls.add(cid)

        if c.get("category") not in cw.mitigation_categories:
            errors.append(f"{cid}: unknown mitigation category '{c.get('category')}'")

        for fw_id, item_ids in (c.get("maps") or {}).items():
            if fw_id not in cw.frameworks:
                errors.append(f"{cid}: maps to unknown framework '{fw_id}'")
                continue
            if len(item_ids) != len(set(item_ids)):
                errors.append(f"{cid}: duplicate item ids under {fw_id}")
            for iid in item_ids:
                if cw.item(fw_id, iid) is None:
                    errors.append(f"{cid}: '{iid}' is not an item of {fw_id}")

        sectors = c.get("sectors") or {}
        for sid in cw.sector_ids:
            if sid not in sectors:
                errors.append(f"{cid}: no priority set for sector '{sid}'")
        for sid, prio in sectors.items():
            if sid not in cw.sector_ids:
                errors.append(f"{cid}: unknown sector '{sid}'")
            if prio not in SECTOR_PRIORITIES:
                errors.append(f"{cid}: sector '{sid}' priority must be one of {SECTOR_PRIORITIES}")
        for sid in (c.get("sector_notes") or {}):
            if sid not in cw.sector_ids:
                errors.append(f"{cid}: sector note for unknown sector '{sid}'")

    return errors
