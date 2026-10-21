import json

import pytest

from crosswalk import analysis
from crosswalk.build import bundle, build_dashboard
from crosswalk.model import load
from crosswalk.validate import validate


@pytest.fixture(scope="module")
def cw():
    return load()


def test_data_is_valid(cw):
    assert validate(cw) == []


def test_expected_framework_sizes(cw):
    sizes = {fid: len(fw["items"]) for fid, fw in cw.frameworks.items()}
    assert sizes["MIT"] == 24          # 7 domains, 24 subdomains
    assert sizes["OWASP-LLM"] == 10
    assert sizes["OWASP-ASI"] == 10
    assert sizes["OECD"] == 5
    assert sizes["ISO42001"] == 38     # Annex A controls
    assert len(cw.mitigation_categories) == 4


@pytest.mark.parametrize("fw", ["OWASP-LLM", "OWASP-ASI", "OECD", "ISO42001", "EUAIA"])
def test_full_coverage_of_actionable_frameworks(cw, fw):
    """Every OWASP risk, OECD principle, ISO control and selected EU AI Act
    article should be addressed by at least one unified control."""
    assert analysis.coverage(cw)[fw]["gaps"] == []


def test_mit_gaps_are_only_systemic_risks(cw):
    """Organisational controls can't fully treat societal / systemic risks -
    keep those visible as gaps instead of forcing a mapping."""
    gaps = set(analysis.coverage(cw)["MIT"]["gaps"])
    assert gaps <= {"MIT-6.1", "MIT-6.3", "MIT-6.4", "MIT-7.5"}


def test_pivot_prompt_injection_to_iso(cw):
    res = analysis.pivot(cw, "LLM01", "ISO42001")
    ids = {t["id"] for t in res["targets"]}
    assert "A.6.2.4" in ids          # verification & validation
    assert "AICC-12" in res["via_controls"]


def test_validator_catches_bad_reference(cw):
    cw.controls[0]["maps"]["ISO42001"].append("A.99.9")
    try:
        assert any("A.99.9" in e for e in validate(cw))
    finally:
        cw.controls[0]["maps"]["ISO42001"].remove("A.99.9")


def test_dashboard_build_inlines_data(cw, tmp_path):
    out = build_dashboard(cw, tmp_path)
    html = out.read_text(encoding="utf-8")
    assert "__CROSSWALK_DATA__" not in html
    data = json.loads((tmp_path / "data.json").read_text(encoding="utf-8"))
    assert len(data["controls"]) == len(cw.controls)
    assert data["coverage"] == json.loads(json.dumps(bundle(cw)["coverage"]))
