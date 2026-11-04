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

When the Vercel deployment is proxied under
`/projects/nvidia-simready-catalog`, set the Vercel environment variable
`NEXT_PUBLIC_ASSET_PREFIX` to `/projects/nvidia-simready-catalog` for the
Preview and Production environments. Leave it unset for a deployment served at
its own domain.

Assets © NVIDIA Corporation, CC-BY-4.0.

## Links

- **GitHub repo:** https://github.com/thisisrick25/nvidia-simready-catalog
- **HF Space:** https://huggingface.co/spaces/thisisrick25/nvidia-simready-catalog · https://thisisrick25-nvidia-simready-catalog.static.hf.space
- **HF Dataset:** https://huggingface.co/datasets/thisisrick25/nvidia-simready-catalog
- **HF Dataset (source):** https://huggingface.co/datasets/nvidia/simready-assets
- **SimReady Foundation:** https://github.com/NVIDIA/simready-foundation
- **Isaac Sim:** https://developer.nvidia.com/isaac/sim