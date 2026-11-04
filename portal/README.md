---
title: SimReady Explorer
emoji: 🤖
colorFrom: green
colorTo: yellow
sdk: static
pinned: false
license: cc-by-4.0
short_description: Interactive catalog for NVIDIA SimReady Assets
---

# SimReady Explorer

Interactive catalog for [nvidia/simready-assets](https://huggingface.co/datasets/nvidia/simready-assets).

Community catalog: asset-level physics (mass, rigid bodies, articulation), category
and size distributions, engine variant coverage (PhysX/MuJoCo/Newton), and SimReady
Foundation validation results. Thumbnails are hotlinked from the original dataset.

This directory is the Next.js source project. The static export is generated in
Next.js's default `out/` directory by:

```bash
npm run build
```

The JSON source data lives in `public/data/` and is copied into the export's
`/data/` path.

Assets © NVIDIA Corporation, CC-BY-4.0.