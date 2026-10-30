# X-ray of a 489.68 GB robotics dataset: what's really inside NVIDIA's SimReady Assets

NVIDIA ships 2,677 simulation-ready 3D assets for robotics on Hugging Face — with no
dataset card. We parsed every one of them without downloading the 489.68 GB. Here's what
the data says. (2026-10-30 snapshot)

## The gap

The `nvidia/simready-assets` dataset on Hugging Face reports ~393k monthly downloads
and 472 GB on the dataset page, but ships with no dataset card — no taxonomy, no
physics summary, no validation status. The size tag on the HF page (472 GB) also
doesn't match what we measured (489.68 GB across 183,394 files). For a dataset this
widely used in robotics simulation, that's a meaningful blind spot.

## How we measured it

We fetched only the ~300 MB of text payloads (`.usda` scene descriptions and
packaging JSONs) via the Hugging Face tree API — no 489.68 GB download. A regex-based
pipeline extracted per-mesh physics (mass, collision approximations, joint limits),
engine variant presence (PhysX / MuJoCo / Newton), and SimReady Foundation validation
results. The pipeline is open source: https://github.com/your-org/simready-catalog

## What's inside

- **14 taxonomy groups** — top categories: `common_assets` (2,314), `props_isaac` (92),
  `props_food` (91), `omniverse` (85), `props_warehouse` (32), `SIM_READY` (32),
  `props_kitchenware` (6), `props_automotive_workshop_tools` (5), `props_softbody` (4),
  `props_endeavor_kitchen` (3), `props_automotive_parts` (2), `props_automotive_equipment` (1),
  `props_kitchen_france` (1), `props_hospital` (1)

- **Mass** runs from **0.0 kg** to **952,461 kg** (median **0.92 kg**). The heaviest assets
  are warehouse structural modules (~950 metric tons); the lightest are blinds, tape,
  and tiny hardware (screws, nuts, bearings) at fractions of a gram.

- **5 articulated assets** (0.2%) — the rest are static props.

- **Engine variants**: PhysX **2,669**, MuJoCo **2,669**, Newton **2,669** — every
  asset ships all three physics flavors in `payloads/{PhysX,MuJoCo,Newton}/`.

![Categories](card/assets/categories.png)
![Mass distribution](card/assets/mass_hist.png)
![Size distribution](card/assets/sizes_hist.png)
![Variants](card/assets/variants.png)
![Validation](card/assets/validation.png)
![Growth](card/assets/growth.png)

## Validation: assets grade themselves

**55.6% pass rate** across SimReady Foundation FET features; most common failing
requirements:

1. `RB.MB.001` — 3,973 failures (rigid-body mass budget)
2. `AA.001` — 3,464 failures (articulation anchor)
3. `VM.MDL.001` — 3,417 failures (material definition)
4. `GSP.001` — 1,190 failures (geometry processing)
5. `NP.008` — 169 failures (naming convention)
6. `HI.009` — 83 failures (hierarchy)
7. `COL.001` — 38 failures (collision)
8. `VM.MAT.001` — 25 failures (material)
9. `RB.001` — 20 failures (rigid body)
10. `NP.005` — 9 failures (naming)

[What FET features mean](https://github.com/NVIDIA/simready-foundation) — the
SimReady Foundation spec defines FET000–FET100 as testable requirements for
simulation readiness (core structure, neutral/PhysX/MuJoCo bases, MDL materials,
Isaac Sim integration).

## Growing daily

Packaging dates run **2026-10-08 → 2026-10-29**, ~10 assets/day on average
(2,138 on the peak day 2026-10-09). Re-run the pipeline any time to refresh.

## Use it

- **Catalog dataset** (card + Parquet tables + stats): `huggingface.co/datasets/<your-namespace>/simready-assets-catalog`
- **Live portal** (Streamlit Space): `huggingface.co/spaces/<your-namespace>/simready-assets-portal`
- **NVIDIA card offer**: see `docs/nvidia-card-offer.md` — post as a discussion on `nvidia/simready-assets`
- **Source pipeline**: https://github.com/your-org/simready-catalog

Assets remain **CC-BY-4.0 © NVIDIA**. This catalog only adds metadata.