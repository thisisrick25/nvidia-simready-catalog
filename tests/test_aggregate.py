import pandas as pd

from pipeline.aggregate import compute_stats


def _assets():
    return pd.DataFrame(
        {
            "asset": ["a_x01", "b_y02"],
            "asset_type": ["prop", "prop"],
            "taxonomy_group": ["props_food", "props_industrial"],
            "variants": [["MuJoCo", "PhysX"], ["PhysX"]],
            "has_articulation": [False, True],
            "mass_kg": [0.5, 100.0],
            "parse_status": ["ok", "ok"],
            "validation_profile": ["Robotics-Prop", "Robotics-Prop"],
            "packaged_date": ["2026-10-01", "2026-10-02"],
            "size_total_bytes": [1000, 2000],
        }
    )


def _meshes():
    return pd.DataFrame(
        {"asset": ["a_x01"], "approximation": ["sdf"], "mass_kg": [0.5]}
    )


def _validation():
    return pd.DataFrame(
        {
            "asset": ["a_x01", "a_x01", "b_y02"],
            "feature": ["FET000_CORE", "FET001_BASE_NEUTRAL", "FET000_CORE"],
            "passed": [True, False, True],
            "failing_requirements": ["[]", "['AA.001']", "[]"],
        }
    )


def _inventory():
    return pd.DataFrame(
        {
            "path": ["a/1", "b/2"],
            "asset": ["a_x01", "b_y02"],
            "size": [1000, 2000],
            "kind": ["payload_usda", "payload_usda"],
            "ext": [".usda", ".usda"],
        }
    )


def test_compute_stats():
    stats = compute_stats(_assets(), _meshes(), _validation(), _inventory())
    assert stats["n_assets"] == 2
    assert stats["n_ok"] == 2
    assert stats["total_size_gb"] == 0.0  # 3000 bytes rounds to 0.00 GB
    assert stats["category_counts"] == {"props_food": 1, "props_industrial": 1}
    assert stats["variant_counts"] == {"PhysX": 2, "MuJoCo": 1}
    assert stats["articulated_count"] == 1
    assert stats["articulated_pct"] == 50.0
    assert stats["mass_stats"]["median"] == 50.25
    assert stats["validation_feature_rates"]["FET000_CORE"] == [2, 2]
    assert stats["validation_feature_rates"]["FET001_BASE_NEUTRAL"] == [0, 1]
    assert stats["validation_pass_rate"] == 66.7
    assert stats["failing_requirements_top"][0] == ("AA.001", 1)
    assert stats["growth_by_date"] == {"2026-10-01": 1, "2026-10-02": 1}
    assert stats["packaged_date_min"] == "2026-10-01"
    assert stats["heaviest10"][0] == ["b_y02", 100.0]
