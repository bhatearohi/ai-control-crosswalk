"""Coverage, gap and pivot analysis over the crosswalk."""
from __future__ import annotations

from collections import defaultdict

from .model import Crosswalk


def controls_for_item(cw: Crosswalk, framework_id: str, item_id: str) -> list[dict]:
    return [c for c in cw.controls if item_id in c["maps"].get(framework_id, [])]


def coverage(cw: Crosswalk, sector: str | None = None, min_priority: str = "low") -> dict[str, dict]:
    """Per framework: how many items are addressed by at least one control.

    If `sector` is given, only controls at or above `min_priority` for that
    sector are counted.
    """
    rank = {"high": 3, "medium": 2, "low": 1}
    controls = [
        c for c in cw.controls
        if sector is None or rank[c["sectors"].get(sector, "low")] >= rank[min_priority]
    ]
    result = {}
    for fw_id in cw.framework_ids:
        items = cw.frameworks[fw_id]["items"]
        covered = {iid for c in controls for iid in c["maps"].get(fw_id, [])}
        result[fw_id] = {
            "total": len(items),
            "covered": sum(1 for i in items if i["id"] in covered),
            "gaps": [i["id"] for i in items if i["id"] not in covered],
        }
        result[fw_id]["percent"] = round(100 * result[fw_id]["covered"] / max(1, len(items)), 1)
    return result


def gaps(cw: Crosswalk) -> dict[str, list[dict]]:
    """Framework items with no mapped control."""
    cov = coverage(cw)
    return {
        fw_id: [cw.item(fw_id, iid) for iid in data["gaps"]]
        for fw_id, data in cov.items() if data["gaps"]
    }


def pivot(cw: Crosswalk, item_id: str, target_framework: str) -> dict:
    """Which items in `target_framework` relate to `item_id` via shared controls?

    Example: pivot(cw, "LLM01", "ISO42001") answers "which ISO 42001 Annex A
    controls help with prompt injection?"
    """
    found = cw.find_item(item_id)
    if not found:
        raise KeyError(f"Unknown item id: {item_id}")
    src_fw, src_item = found
    via = controls_for_item(cw, src_fw, src_item["id"])
    targets: dict[str, list[str]] = defaultdict(list)
    for c in via:
        for tid in c["maps"].get(target_framework, []):
            targets[tid].append(c["id"])
    return {
        "source": {"framework": src_fw, **src_item},
        "via_controls": [c["id"] for c in via],
        "targets": [
            {"id": tid, "title": cw.item(target_framework, tid)["title"], "via": ctrl_ids}
            for tid, ctrl_ids in sorted(targets.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        ],
    }


def risk_heatmap(cw: Crosswalk) -> dict[str, dict[str, int]]:
    """MIT subdomain -> framework -> number of distinct items reachable via controls."""
    out: dict[str, dict[str, int]] = {}
    for risk in cw.frameworks["MIT"]["items"]:
        ctrls = controls_for_item(cw, "MIT", risk["id"])
        row = {}
        for fw_id in cw.framework_ids:
            if fw_id == "MIT":
                continue
            row[fw_id] = len({iid for c in ctrls for iid in c["maps"].get(fw_id, [])})
        row["controls"] = len(ctrls)
        out[risk["id"]] = row
    return out
