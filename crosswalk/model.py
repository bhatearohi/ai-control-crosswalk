"""Load framework, sector and control data from YAML into one Crosswalk object."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# Display order for frameworks in the dashboard and exports.
FRAMEWORK_ORDER = ["MIT", "OWASP-LLM", "OWASP-ASI", "OECD", "ISO42001", "EUAIA"]
SECTOR_PRIORITIES = ("high", "medium", "low")


def _read_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@dataclass
class Crosswalk:
    frameworks: dict[str, dict]            # framework id -> framework metadata + items
    mitigation_categories: dict[str, dict]  # MITM-* id -> category
    sectors: list[dict]
    controls: list[dict]
    version: str = "0"
    _item_index: dict[tuple[str, str], dict] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        for fw_id, fw in self.frameworks.items():
            for item in fw["items"]:
                self._item_index[(fw_id, str(item["id"]))] = item

    # ---- lookups -------------------------------------------------------
    @property
    def framework_ids(self) -> list[str]:
        ordered = [f for f in FRAMEWORK_ORDER if f in self.frameworks]
        return ordered + sorted(f for f in self.frameworks if f not in ordered)

    @property
    def sector_ids(self) -> list[str]:
        return [s["id"] for s in self.sectors]

    def item(self, framework_id: str, item_id: str) -> dict | None:
        return self._item_index.get((framework_id, str(item_id)))

    def control(self, control_id: str) -> dict | None:
        return next((c for c in self.controls if c["id"] == control_id), None)

    def find_item(self, item_id: str) -> tuple[str, dict] | None:
        """Find an item by id across all frameworks (ids are unique by design)."""
        for (fw_id, iid), item in self._item_index.items():
            if iid.lower() == str(item_id).lower():
                return fw_id, item
        return None


def load(data_dir: Path | str = DATA_DIR) -> Crosswalk:
    data_dir = Path(data_dir)
    frameworks: dict[str, dict] = {}
    mitigation_categories: dict[str, dict] = {}

    for path in sorted((data_dir / "frameworks").glob("*.yaml")):
        fw = _read_yaml(path)
        for item in fw["items"]:
            item["id"] = str(item["id"])
        if fw.get("kind") == "mitigation":
            mitigation_categories = {i["id"]: i for i in fw["items"]}
            continue
        frameworks[fw["id"]] = fw

    sectors = _read_yaml(data_dir / "sectors.yaml")["sectors"]
    controls_doc = _read_yaml(data_dir / "controls.yaml")
    controls = controls_doc["controls"]
    for c in controls:
        c["maps"] = {k: [str(v) for v in (vals or [])] for k, vals in (c.get("maps") or {}).items()}
        c.setdefault("sector_notes", {})

    return Crosswalk(
        frameworks=frameworks,
        mitigation_categories=mitigation_categories,
        sectors=sectors,
        controls=controls,
        version=str(controls_doc.get("version", "0")),
    )
