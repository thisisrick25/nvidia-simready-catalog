from pipeline.parse_usda import (
    parse_usda_text, taxonomy, shader_class,
)


def test_header_fields(banana_usda):
    doc = parse_usda_text(banana_usda)
    assert doc["asset_type"] == "prop"
    assert doc["uuid"] == "52d3893b-4fec-4de5-9e6a-af5db79d9b86"
    assert doc["up_axis"] == "Z"
    assert doc["meters_per_unit"] == 1.0


def test_variants(banana_usda):
    doc = parse_usda_text(banana_usda)
    assert doc["variants"] == ["MuJoCo", "Newton", "PhysX"]


def test_validation(banana_usda):
    v = parse_usda_text(banana_usda)["validation"]
    assert v["profile"] == "Robotics-Prop"
    assert v["export_profile"] == "Prop-Robotics-Neutral"
    assert v["profile_version"] == "3.1.0"
    assert v["validated_date"] == "2026-04-28"
    assert len(v["features"]) == 8
    passed = [f for f in v["features"] if f["passed"]]
    assert len(passed) == 4
    fet001 = next(f for f in v["features"] if f["feature"] == "FET001_BASE_NEUTRAL")
    assert fet001["failing_requirements"] == "['AA.001']"


def test_meshes_and_mass(banana_usda):
    doc = parse_usda_text(banana_usda)
    assert doc["mesh_count"] == 1
    assert doc["rigid_body_count"] == 1
    assert abs(doc["total_mass_kg"] - 0.20842493) < 1e-9
    m = doc["meshes"][0]
    assert m["mesh"] == "sm_food_produce_banana_m01_mesh_00"
    assert m["approximation"] == "sdf"
    assert m["material"] == "m_opaque__organic__banana_m01"
    assert "PhysicsMassAPI" in m["api_schemas"]


def test_joints_and_materials(banana_usda):
    doc = parse_usda_text(banana_usda)
    assert doc["has_articulation"] is False
    assert doc["joint_types"] == {}
    assert doc["materials"] == ["m_opaque__organic__banana_m01"]


def test_total_mass_none_when_no_mesh_has_mass():
    text = (
        "#usda 1.0\n"
        "def Xform \"part_a\"\n"
        "{\n"
        "    def Xform \"inner\"\n"
        "    {\n"
        "    }\n"
        "}\n"
    )
    doc = parse_usda_text(text)
    assert doc["mesh_count"] == 2
    assert all(m["mass_kg"] is None for m in doc["meshes"])
    assert doc["total_mass_kg"] is None


def test_total_mass_zero_when_mesh_explicitly_massless():
    text = (
        "#usda 1.0\n"
        "def Xform \"part_a\"\n"
        "{\n"
        "    float physics:mass = 0\n"
        "}\n"
    )
    doc = parse_usda_text(text)
    assert doc["mesh_count"] == 1
    assert doc["meshes"][0]["mass_kg"] == 0.0
    assert doc["total_mass_kg"] == 0.0


def test_taxonomy_and_shader():
    t = taxonomy("simready_content\\common_assets\\props_food\\food_produce_banana_m01\\simready_physx_usd\\sm.usd")
    assert t["root"] == "common_assets"
    assert t["group"] == "props_food"
    assert shader_class("m_opaque__organic__banana_m01") == "opaque"
    assert shader_class("physics_mat_m_opaque__organic__banana_m01") == "opaque"
    assert shader_class(None) is None
