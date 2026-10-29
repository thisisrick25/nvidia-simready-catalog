from pipeline.build_card import render_card


def _stats():
    return {
        "as_of": "2026-10-27",
        "n_assets": 2576,
        "n_ok": 2570,
        "n_parse_errors": 3,
        "n_no_payloads": 3,
        "total_size_gb": 472.0,
        "n_files": 40000,
        "category_counts": {"props_food": 1200, "props_medical": 800},
        "n_categories": 12,
        "asset_type_counts": {"prop": 2400, "robot": 176},
        "variant_counts": {"PhysX": 2500, "MuJoCo": 2400, "Newton": 2300},
        "articulated_count": 300,
        "articulated_pct": 11.6,
        "mass_stats": {"min": 0.01, "median": 2.0, "mean": 40.0, "max": 900.0, "n": 2500},
        "heaviest10": [["engineAssembly_v6_a01", 900.0]],
        "lightest10": [["food_produce_banana_m01", 0.20842493]],
        "validation_profile_counts": {"Robotics-Prop": 2500},
        "validation_feature_rates": {"FET000_CORE": [2400, 2500]},
        "validation_pass_rate": 71.2,
        "failing_requirements_top": [["AA.001", 500]],
        "approximation_counts": {"sdf": 1800, "convexHull": 400},
        "size_mb_stats": {"median": 7.13, "mean": 183.0, "max": 79000.0},
        "packaged_date_min": "2026-09-01",
        "packaged_date_max": "2026-10-27",
        "growth_by_date": {"2026-10-27": 2576},
    }


def test_render_card_structure():
    md = render_card(_stats())
    assert md.startswith("---\n")
    assert "license: cc-by-4.0" in md
    assert "nvidia/simready-assets" in md
    assert "2,576" in md
    assert "472 GB" in md
    assert "payloads" in md
    assert "CC-BY-4.0" in md
    assert "assets/categories.png" in md
    assert "simready-foundation" in md


def test_render_card_handles_sparse_stats():
    md = render_card({"as_of": "2026-10-27", "n_assets": 0, "n_ok": 0,
                     "n_parse_errors": 0, "n_no_payloads": 0, "total_size_gb": 0,
                     "n_files": 0, "category_counts": {}, "n_categories": 0,
                     "asset_type_counts": {}, "variant_counts": {},
                     "articulated_count": 0, "articulated_pct": 0,
                     "mass_stats": None, "heaviest10": [], "lightest10": [],
                     "validation_profile_counts": {},
                     "validation_feature_rates": {}, "validation_pass_rate": None,
                     "failing_requirements_top": [], "approximation_counts": {},
                     "size_mb_stats": None, "packaged_date_min": None,
                     "packaged_date_max": None, "growth_by_date": {}})
    assert "n/a" in md