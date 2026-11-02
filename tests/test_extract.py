import json

import pandas as pd

from pipeline.extract import extract_asset, extract_all


def make_cache(root, banana_usda, banana_pkg):
    a = root / "food_produce_banana_m01"
    (a / "simready_usd" / "payloads").mkdir(parents=True)
    (a / "simready_usd" / "payloads" / "instances_physx.usda").write_text(banana_usda, encoding="utf-8")
    banana_pkg["format_version"] = "1.0"
    (a / "com.nvidia.simready.packaging.json").write_text(json.dumps(banana_pkg), encoding="utf-8")
    metadata = a / ".metadata"
    metadata.mkdir()
    (metadata / "com.nvidia.simready.packaging.bom.json").write_text(
        json.dumps({"files": [{"sha256": "abc"}, {"checksum": "def"}]}),
        encoding="utf-8",
    )
    (metadata / "com.nvidia.simready.conformance.Package@1.0.0.json").write_text(
        "{}", encoding="utf-8"
    )
    empty = root / "empty_asset_x01"
    (empty / "simready_usd").mkdir(parents=True)
    inv = pd.DataFrame(
        [
            {"path": "food_produce_banana_m01/simready_usd/payloads/instances_physx.usda", "asset": "food_produce_banana_m01", "size": 5497, "kind": "payload_usda", "ext": ".usda"},
            {"path": "food_produce_banana_m01/.thumbs/256x256/sm_food_produce_banana_m01_01.usd.png", "asset": "food_produce_banana_m01", "size": 9000, "kind": "thumb_default", "ext": ".png"},
            {"path": "food_produce_banana_m01/.thumbs/256x256/sm_food_produce_banana_m01_01.usd_light.png", "asset": "food_produce_banana_m01", "size": 8000, "kind": "thumb_light", "ext": ".png"},
        ]
    )
    return inv


def test_extract_asset_banana(tmp_path, banana_usda, banana_pkg):
    inv = make_cache(tmp_path, banana_usda, banana_pkg)
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
    assert "resolve/main" in row["thumb_url"] and row["thumb_url"].endswith(".usd.png")
    assert row["metadata_file_count"] == 2
    assert row["bom_file_count"] == 1
    assert row["bom_entry_count"] == 2
    assert row["bom_hash_count"] == 2
    assert row["package_hash_count"] == 2
    assert row["package_format_version"] == "1.0"
    assert row["conformance_versions"] == "1.0.0"
    assert len(meshes) == 1 and len(vals) == 8 and len(mats) == 1
    assert mats[0]["shader_class"] == "opaque"
    assert mats[0]["semantic_tokens"] == "organic"


def test_extract_asset_no_payloads(tmp_path, banana_usda, banana_pkg):
    inv = make_cache(tmp_path, banana_usda, banana_pkg)
    row, meshes, vals, mats = extract_asset(tmp_path / "empty_asset_x01", inv)
    assert row["parse_status"] == "no_payloads"
    assert meshes == [] and vals == []


def test_extract_all_writes_parquets(tmp_path, banana_usda, banana_pkg):
    inv = make_cache(tmp_path / "cache", banana_usda, banana_pkg)
    out = tmp_path / "data"
    assets = extract_all(tmp_path / "cache", inv, out)
    assert len(assets) == 2
    for f in ("assets", "meshes", "validation", "materials"):
        assert (out / f"{f}.parquet").exists()


def test_extract_asset_falls_back_to_newton_payload(tmp_path, banana_usda):
    a = tmp_path / "food_produce_banana_m01"
    (a / "simready_usd" / "payloads").mkdir(parents=True)
    (a / "simready_usd" / "payloads" / "instances_newton.usda").write_text(banana_usda, encoding="utf-8")
    row, meshes, vals, mats = extract_asset(a, pd.DataFrame())
    assert row["parse_status"] == "ok"
    assert abs(row["mass_kg"] - 0.20842493) < 1e-9
    assert len(meshes) == 1


def test_extract_asset_no_physics_payload(tmp_path):
    a = tmp_path / "no_physics_x01"
    (a / "simready_usd" / "payloads").mkdir(parents=True)
    (a / "simready_usd" / "payloads" / "base.usda").write_text("#usda 1.0\n", encoding="utf-8")
    (a / "simready_usd" / "payloads" / "materials.usda").write_text("#usda 1.0\n", encoding="utf-8")
    row, meshes, vals, mats = extract_asset(a, pd.DataFrame())
    assert row["parse_status"] == "no_physics_payload"
    assert row["parse_error"] and "base.usda" in row["parse_error"] and "materials.usda" in row["parse_error"]
    assert meshes == [] and vals == []


def test_extract_asset_parse_error_never_crashes(tmp_path):
    a = tmp_path / "broken_asset_x01"
    payloads = a / "simready_usd" / "payloads"
    payloads.mkdir(parents=True)
    (payloads / "instances_physx.usda").mkdir()
    row, meshes, vals, mats = extract_asset(a, pd.DataFrame())
    assert row["parse_status"] == "parse_error"
    assert row["parse_error"]
    assert meshes == [] and vals == []


def test_extract_asset_merges_articulation_from_base(tmp_path, banana_usda):
    a = tmp_path / "articulated_x01"
    (a / "simready_usd" / "payloads").mkdir(parents=True)
    (a / "simready_usd" / "payloads" / "instances_physx.usda").write_text(banana_usda, encoding="utf-8")
    base_usda = (
        "#usda 1.0\n"
        "def PhysicsRevoluteJoint \"joint_0\" (\n"
        "    prepend apiSchemas = [\"PhysicsArticulationRootAPI\"]\n"
        ")\n"
        "{\n"
        "}\n"
    )
    (a / "simready_usd" / "payloads" / "base.usda").write_text(base_usda, encoding="utf-8")
    row, meshes, vals, mats = extract_asset(a, pd.DataFrame())
    assert row["parse_status"] == "ok"
    assert row["has_articulation"] is True
    assert json.loads(row["joint_types"]) == {"revolute": 1}
