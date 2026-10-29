import json
from pathlib import Path

import pandas as pd

from pipeline.extract import extract_asset, extract_all

FIXTURES = Path(__file__).parent / "fixtures"
BANANA_USDA = (FIXTURES / "instances_physx_banana.usda").read_text(encoding="utf-8")
BANANA_PKG = json.loads((FIXTURES / "packaging_banana.json").read_text(encoding="utf-8"))


def make_cache(root: Path):
    a = root / "food_produce_banana_m01"
    (a / "simready_usd" / "payloads").mkdir(parents=True)
    (a / "simready_usd" / "payloads" / "instances_physx.usda").write_text(BANANA_USDA, encoding="utf-8")
    (a / "com.nvidia.simready.packaging.json").write_text(json.dumps(BANANA_PKG), encoding="utf-8")
    empty = root / "empty_asset_x01"
    (empty / "simready_usd").mkdir(parents=True)
    inv = pd.DataFrame(
        [
            {"path": "food_produce_banana_m01/simready_usd/payloads/instances_physx.usda", "asset": "food_produce_banana_m01", "size": 5497, "kind": "payload_usda", "ext": ".usda"},
            {"path": "food_produce_banana_m01/.thumbs/256x256/sm_food_produce_banana_m01_01_usd_lit.png", "asset": "food_produce_banana_m01", "size": 9000, "kind": "thumb_lit", "ext": ".png"},
            {"path": "food_produce_banana_m01/.thumbs/256x256/sm_food_produce_banana_m01_01_usd_unlit.png", "asset": "food_produce_banana_m01", "size": 8000, "kind": "thumb_unlit", "ext": ".png"},
        ]
    )
    return inv


def test_extract_asset_banana(tmp_path):
    inv = make_cache(tmp_path)
    row, meshes, vals, mats = extract_asset(tmp_path / "food_produce_banana_m01", inv)
    assert row["parse_status"] == "ok"
    assert abs(row["mass_kg"] - 0.20842493) < 1e-9
    assert row["rigid_body_count"] == 1
    assert row["variants"] == ["MuJoCo", "Newton", "PhysX"]
    assert row["taxonomy_group"] == "props_food"
    assert row["features_total"] == 8 and row["features_passed"] == 4
    assert row["all_features_passed"] is False
    assert row["license"] == "CC-BY-4.0"
    assert row["packaged_date"] == "2026-10-09"
    assert "resolve/main" in row["thumb_url"] and "unlit" not in row["thumb_url"]
    assert len(meshes) == 1 and len(vals) == 8 and len(mats) == 1
    assert mats[0]["shader_class"] == "opaque"
    assert mats[0]["semantic_tokens"] == "organic"


def test_extract_asset_no_payloads(tmp_path):
    inv = make_cache(tmp_path)
    row, meshes, vals, mats = extract_asset(tmp_path / "empty_asset_x01", inv)
    assert row["parse_status"] == "no_payloads"
    assert meshes == [] and vals == []


def test_extract_all_writes_parquets(tmp_path):
    inv = make_cache(tmp_path / "cache")
    out = tmp_path / "data"
    assets = extract_all(tmp_path / "cache", inv, out)
    assert len(assets) == 2
    for f in ("assets", "meshes", "validation", "materials"):
        assert (out / f"{f}.parquet").exists()