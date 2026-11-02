import json
import logging
from pathlib import Path

from pipeline.config import CARD_DIR, DATA_DIR

logger = logging.getLogger(__name__)


def _fmt_int(n):
    return f"{int(n):,}" if n is not None else "n/a"


def _table(rows, headers):
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for r in rows:
        lines.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(lines)


def render_card(stats) -> str:
    n = stats.get("n_assets")
    ms = stats.get("mass_stats") or {}
    vc = stats.get("variant_counts") or {}
    rates = stats.get("validation_feature_rates") or {}
    fails = stats.get("failing_requirements_top") or []
    cats = stats.get("category_counts") or {}
    approx = stats.get("approximation_counts") or {}
    size = stats.get("size_mb_stats") or {}

    total_gb = stats.get('total_size_gb', 0)
    total_gb_str = f"{total_gb:g}"
    at_a_glance = _table(
        [
            ["Assets", _fmt_int(n)],
            ["Total size", f"{total_gb_str} GB"],
            ["Files", _fmt_int(stats.get("n_files"))],
            ["Categories", _fmt_int(stats.get("n_categories"))],
            ["Articulated assets", f"{_fmt_int(stats.get('articulated_count'))} ({stats.get('articulated_pct', 0)}%)"],
            ["PhysX variant", _fmt_int(vc.get("PhysX"))],
            ["MuJoCo variant", _fmt_int(vc.get("MuJoCo"))],
            ["Newton variant", _fmt_int(vc.get("Newton"))],
            ["License", "CC-BY-4.0"],
            ["Data as of", stats.get("as_of", "n/a")],
        ],
        ["", ""],
    )

    physics_rows = []
    if ms:
        physics_rows = [
            ["Minimum", f"{ms['min']:g} kg"],
            ["Median", f"{ms['median']:g} kg"],
            ["Mean", f"{ms['mean']:g} kg"],
            ["Maximum", f"{ms['max']:g} kg"],
        ]
    physics_table = _table(physics_rows, ["Mass (per-asset sum)", "Value"]) if physics_rows else "_No mass data parsed._"

    outliers_n = stats.get("mass_outliers_count") or 0
    outlier_note = ""
    if outliers_n:
        threshold = stats.get("mass_outlier_threshold_kg", 0)
        pct = stats.get("mass_outliers_pct", 0)
        outlier_note = (
            f"\n> [!WARNING]\n"
            f"> **Known data quality note:** {_fmt_int(outliers_n)} assets ({pct}%) report a "
            f"summed mass above {threshold:g} kg (e.g. warehouse structural modules, an exhaust "
            f"manifold at ~500,000 kg) — these look like authoring/export defects in NVIDIA's "
            f"source USD rather than real weights. We report the numbers as-is, unmodified; use "
            f"the **median** above rather than the mean when reasoning about a typical asset.\n"
        )

    heaviest = _table(
        [[a, f"{m:g}"] for a, m in (stats.get("heaviest10") or [])],
        ["Asset", "Mass (kg)"],
    )
    lightest = _table(
        [[a, f"{m:g}"] for a, m in (stats.get("lightest10") or [])],
        ["Asset", "Mass (kg)"],
    )

    validation_rows = [
        [k, f"{100 * p / t:.1f}%" if t else "n/a", f"{p:,} / {t:,}"]
        for k, (p, t) in sorted(rates.items())
    ]
    validation_table = (
        _table(validation_rows, ["Feature", "Pass rate", "Passed / total"])
        if validation_rows
        else "_No validation data parsed._"
    )

    fail_rows = [[req, _fmt_int(cnt)] for req, cnt in fails]
    fails_table = _table(fail_rows, ["Failing requirement", "Occurrences"]) if fail_rows else "_None._"

    cat_rows = [[k, _fmt_int(v)] for k, v in list(cats.items())[:20]]
    cats_table = _table(cat_rows, ["Category (taxonomy group)", "Assets"]) if cat_rows else "_n/a_"

    approx_str = ", ".join(f"`{k}` ({_fmt_int(v)})" for k, v in sorted(approx.items())) or "_n/a_"
    growth_line = (
        f"{stats.get('packaged_date_min')} \u2192 {stats.get('packaged_date_max')}"
        if stats.get("packaged_date_min")
        else "n/a"
    )

    return f"""---
license: cc-by-4.0
task_categories:
- robotics
tags:
- robotics
- simulation
- OpenUSD
- Isaac-Sim
- synthetic-data
- physics
- mujoco
size_categories:
- 1K<n<10K
pretty_name: SimReady Assets (NVIDIA)
---

# NVIDIA SimReady Assets \u2014 Community Dataset Card

> [!NOTE]
> This card was produced by the community catalog project and offered to NVIDIA; numbers are computed programmatically from the repo tree and payload files on {stats.get('as_of', 'n/a')}. Verify against https://huggingface.co/datasets/nvidia/simready-assets for the latest state.

NVIDIA's **SimReady Assets** are simulation-ready 3D models for robotics and Physical AI: every asset ships with tuned physics (mass, inertia, collision approximations), materials, and variants for **PhysX**, **MuJoCo**, and **Newton** physics engines. The dataset contains **{_fmt_int(n)} assets** totaling **{total_gb_str} GB** under **CC-BY-4.0**.

## Dataset at a glance

{at_a_glance}

## Directory structure

Each asset lives in its own top-level directory:

```
<asset_name>/
├── com.nvidia.simready.packaging.json   # package id, license, sha256 hashes
├── .metadata/                           # bill of materials
├── simready_usd/
│   ├── sm_<asset_name>_01.usd           # main SimReady USD (binary USDC)
│   ├── payloads/
│   │   ├── base.usda                    # structure + variant sets
│   │   ├── instances.usda               # per-mesh physics (neutral)
│   │   ├── instances_physx.usda          # per-mesh physics (PhysX)
│   │   ├── instances_mujoco.usda         # per-mesh physics (MuJoCo)
│   │   ├── instances_newton.usda         # per-mesh physics (Newton)
│   │   ├── materials.usda                # material definitions
│   │   ├── geometries.usd                # mesh data (the big file)
│   │   └── PhysX/ MuJoCo/ Newton/ Physics/   # engine payload subdirs
│   ├── source_assets/                    # original DCC files
│   └── Textures/
└── .thumbs/256x256/                     # rendered thumbnails (lit/unlit)
```

**Tip:** for metadata and physics you only need the small text `.usda` payload files; `geometries.usd` holds the mesh data and dominates download size.

## Naming conventions

Asset names follow `<category>_<type>_<variant>` (e.g. `food_produce_banana_m01`, `appliance_dishwasher_a01`). Variant suffixes (`a01`, `b01`, `m01`, ...) distinguish design variants of the same object type. See NVIDIA's naming guide in the [simready-foundation](https://github.com/NVIDIA/simready-foundation) repo for the authoritative conventions.

## What's in the catalog

{cats_table}

![Assets per category](assets/categories.png)

## Physics

Per-mesh physics properties (`physics:mass`, `physics:centerOfMass`, `physics:diagonalInertia`, collision `physics:approximation`) are authored in the `instances_*.usda` payloads. Asset mass below is the sum of per-mesh masses from the PhysX instance file.

{physics_table}
{outlier_note}
Collision approximations in use: {approx_str}

![Mass distribution](assets/mass_hist.png)
![Download size](assets/sizes_hist.png)

### Heaviest assets

{heaviest}

### Lightest assets

{lightest}

## Physics engine variants

Each asset declares MuJoCo / Newton / PhysX physics variants in `base.usda` (`Variants \u2192 Physics`), so the same asset can be simulated in any of the three engines:

![Variant coverage](assets/variants.png)

## Validation (SimReady Foundation)

Assets embed their own validation results (`SimReady_Metadata \u2192 validation`), produced by NVIDIA's [simready-foundation](https://github.com/NVIDIA/simready-foundation) tooling against the `Robotics-Prop` profile. Overall pass rate across parsed validation rows: **{stats.get('validation_pass_rate') if stats.get('validation_pass_rate') is not None else 'n/a'}%**.

{validation_table}

Most common failing requirements:

{fails_table}

![Validation pass rates](assets/validation.png)

## Growth

Packaging dates extracted from package IDs run {growth_line}:

![Growth](assets/growth.png)

## How to use

**Isaac Sim / Omniverse:** add the dataset as a local or cloud asset root; `sm_*.usd` files are drop-in placeable with physics already tuned.

**Plain OpenUSD (Python):**
```python
# pip install usd-core
from pxr import Usd, UsdPhysics
stage = Usd.Stage.Open("food_produce_banana_m01/simready_usd/sm_food_produce_banana_m01_01.usd")
for prim in stage.Traverse():
    mass = UsdPhysics.MassAPI(prim)
    if mass:
        print(prim.GetPath(), mass.GetMassAttr().Get())
```

**MuJoCo / Newton:** load the same `sm_*.usd` and activate the MuJoCo (or Newton) physics variant; or use `payloads/instances_mujoco.usda` directly.

## License & attribution

The assets are \u00a9 NVIDIA Corporation, licensed [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). When using assets (or derived data such as this catalog), credit "NVIDIA SimReady Assets" and link to https://huggingface.co/datasets/nvidia/simready-assets.

## Citation

```bibtex
@dataset{{nvidia_simready_assets,
  title  = {{NVIDIA SimReady Assets}},
  author = {{NVIDIA Corporation}},
  year   = {{2026}},
  url    = {{https://huggingface.co/datasets/nvidia/simready-assets}},
  license = {{CC-BY-4.0}}
}}
```

## Companion resources

- **Catalog parquets** (per-asset physics/validation/size tables): see this project's companion dataset
- **Interactive stats portal**: see this project's Space
- **SimReady Foundation** (validation specs & tooling): https://github.com/NVIDIA/simready-foundation
- **Isaac Sim**: https://developer.nvidia.com/isaac/sim

_Generated from repository data as of {stats.get('as_of', 'n/a')}; the dataset grows daily \u2014 re-run the pipeline for fresh numbers._
"""


def main():
    stats = json.loads((DATA_DIR / "stats.json").read_text(encoding="utf-8"))
    md = render_card(stats)
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    (CARD_DIR / "README.md").write_text(md, encoding="utf-8")
    logger.info("card -> %s (%d chars)", CARD_DIR / "README.md", len(md))


if __name__ == "__main__":
    main()
