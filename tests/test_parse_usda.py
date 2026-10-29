from pathlib import Path

from pipeline.parse_usda import (
    parse_usda_text, taxonomy, shader_class,
)

FIXTURES = Path(__file__).parent / "fixtures"
BANANA = (FIXTURES / "instances_physx_banana.usda").read_text(encoding="utf-8")


def test_header_fields():
    doc = parse_usda_text(BANANA)
    assert doc["asset_type"] == "prop"
    assert doc["uuid"] == "52d3893b-4fec-4de5-9e6a-af5db79d9b86"
    assert doc["up_axis"] == "Z"
    assert doc["meters_per_unit"] == 1.0


def test_variants():
    doc = parse_usda_text(BANANA)
    assert doc["variants"] == ["MuJoCo", "Newton", "PhysX"]


def test_validation():
    v = parse_usda_text(BANANA)["validation"]
    assert v["profile"] == "Robotics-Prop"
    assert v["export_profile"] == "Prop-Robotics-Neutral"
    assert v["profile_version"] == "3.1.0"
    assert v["validated_date"] == "2026-04-28"
    assert len(v["features"]) == 8
    passed = [f for f in v["features"] if f["passed"]]
    assert len(passed) == 4
    fet001 = next(f for f in v["features"] if f["feature"] == "FET001_BASE_NEUTRAL")
    assert fet001["failing_requirements"] == "['AA.001']"


def test_meshes_and_mass():
    doc = parse_usda_text(BANANA)
    assert doc["mesh_count"] == 1
    assert doc["rigid_body_count"] == 1
    assert abs(doc["total_mass_kg"] - 0.20842493) < 1e-9
    m = doc["meshes"][0]
    assert m["mesh"] == "sm_food_produce_banana_m01_mesh_00"
    assert m["approximation"] == "sdf"
    assert m["material"] == "m_opaque__organic__banana_m01"
    assert "PhysicsMassAPI" in m["api_schemas"]


def test_joints_and_materials():
    doc = parse_usda_text(BANANA)
    assert doc["has_articulation"] is False
    assert doc["joint_types"] == {}
    assert doc["materials"] == ["m_opaque__organic__banana_m01"]


def test_taxonomy_and_shader():
    t = taxonomy("simready_content\\common_assets\\props_food\\food_produce_banana_m01\\simready_physx_usd\\sm.usd")
    assert t["root"] == "common_assets"
    assert t["group"] == "props_food"
    assert shader_class("m_opaque__organic__banana_m01") == "opaque"
    assert shader_class("physics_mat_m_opaque__organic__banana_m01") == "opaque"
    assert shader_class(None) is None