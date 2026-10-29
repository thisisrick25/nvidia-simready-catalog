---
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

# NVIDIA SimReady Assets — Community Dataset Card

> [!NOTE]
> This card was produced by the community catalog project and offered to NVIDIA; numbers are computed programmatically from the repo tree and payload files on 2026-10-30. Verify against https://huggingface.co/datasets/nvidia/simready-assets for the latest state.

NVIDIA's **SimReady Assets** are simulation-ready 3D models for robotics and Physical AI: every asset ships with tuned physics (mass, inertia, collision approximations), materials, and variants for **PhysX**, **MuJoCo**, and **Newton** physics engines. The dataset contains **20 assets** totaling **489.36 GB** under **CC-BY-4.0**.

## Dataset at a glance

|  |  |
|---|---|
| Assets | 20 |
| Total size | 489.36 GB |
| Files | 183,200 |
| Categories | 1 |
| Articulated assets | 0 (0.0%) |
| PhysX variant | 20 |
| MuJoCo variant | 20 |
| Newton variant | 20 |
| License | CC-BY-4.0 |
| Data as of | 2026-10-30 |

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

| Category (taxonomy group) | Assets |
|---|---|
| common_assets | 20 |

![Assets per category](assets/categories.png)

## Physics

Per-mesh physics properties (`physics:mass`, `physics:centerOfMass`, `physics:diagonalInertia`, collision `physics:approximation`) are authored in the `instances_*.usda` payloads. Asset mass below is the sum of per-mesh masses from the PhysX instance file.

| Mass (per-asset sum) | Value |
|---|---|
| Minimum | 0.175078 kg |
| Median | 2.79144 kg |
| Mean | 18.0471 kg |
| Maximum | 183.045 kg |

Collision approximations in use: `sdf` (193)

![Mass distribution](assets/mass_hist.png)
![Download size](assets/sizes_hist.png)

### Heaviest assets

| Asset | Mass (kg) |
|---|---|
| Xray_machine_XrayArmRack_a01 | 183.045 |
| Xray_machine_buckyTable_a01 | 36.9376 |
| TV_a01 | 35.2989 |
| CT_injection_system_a01 | 25.3864 |
| Xray_machine_HVgenerator_a01 | 16.0634 |
| Xray_machine_buckyStand_a01 | 13.0065 |
| IV_pole_b01 | 12.5503 |
| airSystem_compressor_a01 | 11.3487 |
| IV_pole_b03 | 9.76659 |
| airSystem_air_filter_box_c01 | 2.97001 |

### Lightest assets

| Asset | Mass (kg) |
|---|---|
| accessory_eyeglasses_a01 | 0.175078 |
| airSystem_air_filter_a01 | 0.29873 |
| airSystem_air_filter_c01 | 0.397438 |
| airSystem_air_filter_box_a01 | 1.50709 |
| IV_pole_a03 | 1.59252 |
| IV_pole_a04 | 1.61199 |
| IV_pole_a02 | 1.62116 |
| airSystem_air_filter_box_d01 | 2.24451 |
| IV_pole_b02 | 2.50808 |
| IV_pole_a01 | 2.61286 |

## Physics engine variants

Each asset declares MuJoCo / Newton / PhysX physics variants in `base.usda` (`Variants → Physics`), so the same asset can be simulated in any of the three engines:

![Variant coverage](assets/variants.png)

## Validation (SimReady Foundation)

Assets embed their own validation results (`SimReady_Metadata → validation`), produced by NVIDIA's [simready-foundation](https://github.com/NVIDIA/simready-foundation) tooling against the `Robotics-Prop` profile. Overall pass rate across parsed validation rows: **59.8%**.

| Feature | Pass rate | Passed / total |
|---|---|---|
| FET000_CORE | 100.0% | 27 / 27 |
| FET001_BASE_NEUTRAL | 0.0% | 0 / 30 |
| FET003_BASE_NEUTRAL | 100.0% | 30 / 30 |
| FET003_BASE_PHYSX | 100.0% | 30 / 30 |
| FET004_BASE_NEUTRAL | 73.3% | 22 / 30 |
| FET004_BASE_PHYSX | 73.3% | 22 / 30 |
| FET005_BASE_NEUTRAL | 30.0% | 9 / 30 |
| FET006_BASE_MDL | 0.0% | 0 / 27 |

Most common failing requirements:

| Failing requirement | Occurrences |
|---|---|
| AA.001 | 30 |
| VM.MDL.001 | 27 |
| GSP.001 | 21 |
| RB.MB.001 | 16 |

![Validation pass rates](assets/validation.png)

## Growth

Packaging dates extracted from package IDs run 2026-10-08 → 2026-10-13:

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

The assets are © NVIDIA Corporation, licensed [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). When using assets (or derived data such as this catalog), credit "NVIDIA SimReady Assets" and link to https://huggingface.co/datasets/nvidia/simready-assets.

## Citation

```bibtex
@dataset{nvidia_simready_assets,
  title  = {NVIDIA SimReady Assets},
  author = {NVIDIA Corporation},
  year   = {2026},
  url    = {https://huggingface.co/datasets/nvidia/simready-assets},
  license = {CC-BY-4.0}
}
```

## Companion resources

- **Catalog parquets** (per-asset physics/validation/size tables): see this project's companion dataset
- **Interactive stats portal**: see this project's Space
- **SimReady Foundation** (validation specs & tooling): https://github.com/NVIDIA/simready-foundation
- **Isaac Sim**: https://developer.nvidia.com/isaac/sim

_Generated from repository data as of 2026-10-30; the dataset grows daily — re-run the pipeline for fresh numbers._
