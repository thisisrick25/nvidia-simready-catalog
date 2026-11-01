import ast
import json
from collections import Counter
from datetime import date

import pandas as pd

from pipeline.config import DATA_DIR

# Heuristic ceiling for a single asset's summed mass. A handful of upstream
# NVIDIA payload files carry physically implausible physics:mass values
# (e.g. a single exhaust-manifold part at ~500,000 kg) that are almost
# certainly authoring/export defects, not legitimate weights. We never
# mutate the source data - we only report how many assets exceed this
# threshold so downstream readers can judge the mean/max with that context.
MASS_OUTLIER_THRESHOLD_KG = 5000.0


def compute_stats(assets, meshes, validation, inventory):
    stats = {"as_of": date.today().isoformat()}
    stats["n_assets"] = int(len(assets))
    stats["n_ok"] = int((assets["parse_status"] == "ok").sum())
    stats["n_parse_errors"] = int((assets["parse_status"] == "parse_error").sum())
    stats["n_no_payloads"] = int((assets["parse_status"] == "no_payloads").sum())
    stats["n_no_physics_payload"] = int(
        (assets["parse_status"] == "no_physics_payload").sum()
    )
    stats["total_size_gb"] = round(float(inventory["size"].sum()) / 1e9, 2)
    stats["n_files"] = int(len(inventory))

    cats = assets["taxonomy_group"].value_counts()
    stats["category_counts"] = {str(k): int(v) for k, v in cats.items()}
    stats["n_categories"] = int(cats.shape[0])
    stats["asset_type_counts"] = {
        str(k): int(v)
        for k, v in assets["asset_type"].value_counts(dropna=False).items()
    }

    vc = Counter()
    for v in assets["variants"].dropna():
        vc.update(v)
    stats["variant_counts"] = dict(vc)

    stats["articulated_count"] = int(assets["has_articulation"].fillna(False).sum())
    stats["articulated_pct"] = round(
        100 * stats["articulated_count"] / max(stats["n_assets"], 1), 1
    )

    mass = pd.to_numeric(assets["mass_kg"], errors="coerce").dropna()
    if len(mass):
        outliers = mass[mass > MASS_OUTLIER_THRESHOLD_KG]
        stats["mass_stats"] = {
            "min": float(mass.min()),
            "median": float(mass.median()),
            "mean": round(float(mass.mean()), 4),
            "max": float(mass.max()),
            "n": int(len(mass)),
        }
        stats["mass_outlier_threshold_kg"] = MASS_OUTLIER_THRESHOLD_KG
        stats["mass_outliers_count"] = int(len(outliers))
        stats["mass_outliers_pct"] = round(100 * len(outliers) / len(mass), 2)
        ranked = assets.dropna(subset=["mass_kg"])
        stats["heaviest10"] = ranked.nlargest(10, "mass_kg")[
            ["asset", "mass_kg"]
        ].values.tolist()
        stats["lightest10"] = ranked.nsmallest(10, "mass_kg")[
            ["asset", "mass_kg"]
        ].values.tolist()
    else:
        stats["mass_stats"] = None
        stats["mass_outlier_threshold_kg"] = MASS_OUTLIER_THRESHOLD_KG
        stats["mass_outliers_count"] = 0
        stats["mass_outliers_pct"] = 0.0
        stats["heaviest10"] = []
        stats["lightest10"] = []

    stats["validation_profile_counts"] = {
        str(k): int(v)
        for k, v in assets["validation_profile"].value_counts(dropna=False).items()
    }

    if len(validation):
        g = validation.groupby("feature")["passed"].agg(["sum", "count"])
        stats["validation_feature_rates"] = {
            str(k): [int(r["sum"]), int(r["count"])] for k, r in g.iterrows()
        }
        stats["validation_pass_rate"] = round(100 * validation["passed"].mean(), 1)
        c = Counter()
        for s in validation.loc[~validation["passed"], "failing_requirements"].dropna():
            try:
                c.update(ast.literal_eval(s))
            except Exception:
                pass
        stats["failing_requirements_top"] = c.most_common(15)
    else:
        stats["validation_feature_rates"] = {}
        stats["validation_pass_rate"] = None
        stats["failing_requirements_top"] = []

    if len(meshes):
        approx = meshes["approximation"].value_counts()
        stats["approximation_counts"] = {str(k): int(v) for k, v in approx.items()}
    else:
        stats["approximation_counts"] = {}

    sizes = pd.to_numeric(assets["size_total_bytes"], errors="coerce").dropna()
    sizes = sizes[sizes > 0]
    if len(sizes):
        mb = sizes / 1e6
        stats["size_mb_stats"] = {
            "median": round(float(mb.median()), 2),
            "mean": round(float(mb.mean()), 2),
            "max": round(float(mb.max()), 2),
        }
    else:
        stats["size_mb_stats"] = None

    dates = assets["packaged_date"].dropna()
    if len(dates):
        stats["packaged_date_min"] = str(dates.min())
        stats["packaged_date_max"] = str(dates.max())
        growth = dates.value_counts().sort_index()
        stats["growth_by_date"] = {str(k): int(v) for k, v in growth.items()}
    else:
        stats["packaged_date_min"] = None
        stats["packaged_date_max"] = None
        stats["growth_by_date"] = {}
    return stats


def main():
    assets = pd.read_parquet(DATA_DIR / "assets.parquet")
    meshes = pd.read_parquet(DATA_DIR / "meshes.parquet")
    validation = pd.read_parquet(DATA_DIR / "validation.parquet")
    inventory = pd.read_parquet(DATA_DIR / "inventory.parquet")
    stats = compute_stats(assets, meshes, validation, inventory)
    (DATA_DIR / "stats.json").write_text(
        json.dumps(stats, indent=2), encoding="utf-8"
    )
    print(
        f"stats -> {DATA_DIR / 'stats.json'} "
        f"({stats['n_assets']} assets, {stats['n_categories']} categories)"
    )
    return stats


if __name__ == "__main__":
    main()
