import json
from pathlib import Path

from pipeline.parse_packaging import parse_packaging, deploy_date_from_package_id

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_packaging_returns_dict():
    text = (FIXTURES / "packaging_banana.json").read_text(encoding="utf-8")
    data = parse_packaging(text)
    assert data["license"] == "CC-BY-4.0"
    assert data["format_version"] == "1.0"
    assert "food_produce_banana_m01" in data["package_id"]


def test_parse_packaging_bad_json():
    assert parse_packaging("{not json") is None


def test_deploy_date_from_package_id():
    pid = "simready.hf.nvidia.simready-assets.food_produce_banana_m01.2026.10.09_141223"
    assert deploy_date_from_package_id(pid) == "2026-10-09"
    assert deploy_date_from_package_id(None) is None
    assert deploy_date_from_package_id("no-date-here") is None