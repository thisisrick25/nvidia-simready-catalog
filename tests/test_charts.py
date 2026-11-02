import pandas as pd

from pipeline.charts import make_charts


def _stats():
    return {
        "category_counts": {"props_food": 1200, "props_medical": 800},
        "variant_counts": {"PhysX": 2500, "MuJoCo": 2400, "Newton": 2300},
        "validation_feature_rates": {"FET000_CORE": [2400, 2500], "FET001_BASE_NEUTRAL": [1500, 2500]},
        "growth_by_date": {"2026-09-01": 40, "2026-10-01": 80},
    }


def test_make_charts_creates_pngs(tmp_path):
    assets = pd.DataFrame({"mass_kg": [0.2, 1.0, 50.0], "size_total_bytes": [7e6, 79e6, 2e6]})
    created = make_charts(assets, _stats(), tmp_path)
    names = {p.name for p in created}
    assert names == {"categories.png", "mass_hist.png", "sizes_hist.png", "variants.png", "validation.png", "growth.png"}
    for p in created:
        assert p.exists() and p.stat().st_size > 1000


def test_make_charts_with_zero_mass(tmp_path):
    assets = pd.DataFrame({"mass_kg": [0.0, 0.2, 1.0], "size_total_bytes": [1e6, 2e6, 3e6]})
    created = make_charts(assets, _stats(), tmp_path)
    names = {p.name for p in created}
    assert "mass_hist.png" in names
    assert (tmp_path / "mass_hist.png").stat().st_size > 1000


def test_make_charts_empty_inputs(tmp_path):
    created = make_charts(pd.DataFrame(dtype=float), {}, tmp_path)
    assert created == []
