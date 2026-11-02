import json
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pipeline.config import DATA_DIR

logger = logging.getLogger(__name__)
NVIDIA_GREEN = "#76b900"


def _save(fig, outdir, name):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / name
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def make_charts(assets, stats, outdir):
    created = []

    cats = stats.get("category_counts") or {}
    if cats:
        items = list(cats.items())[:25][::-1]
        fig, ax = plt.subplots(figsize=(8, max(4, 0.32 * len(items))))
        ax.barh([k for k, _ in items], [v for _, v in items], color=NVIDIA_GREEN)
        ax.set_title("Assets per category (top 25)")
        ax.set_xlabel("assets")
        created.append(_save(fig, outdir, "categories.png"))

    if "mass_kg" in assets:
        mass = pd.to_numeric(assets["mass_kg"], errors="coerce").dropna()
        mass = mass[mass > 0]
        if len(mass):
            fig, ax = plt.subplots(figsize=(8, 4.5))
            lo = float(mass.min())
            bins = np.logspace(np.log10(lo), np.log10(float(mass.max()) * 1.01), 40)
            ax.hist(mass, bins=bins, color=NVIDIA_GREEN)
            ax.set_xscale("log")
            ax.set_title("Total physics mass per asset (kg, log scale)")
            ax.set_xlabel("kg")
            ax.set_ylabel("assets")
            created.append(_save(fig, outdir, "mass_hist.png"))

    if "size_total_bytes" in assets:
        sizes = pd.to_numeric(assets["size_total_bytes"], errors="coerce").dropna()
        mb = sizes[sizes > 0] / 1e6
        if len(mb):
            fig, ax = plt.subplots(figsize=(8, 4.5))
            lo = max(float(mb.min()), 1e-3)
            bins = np.logspace(np.log10(lo), np.log10(float(mb.max()) * 1.01), 40)
            ax.hist(mb, bins=bins, color=NVIDIA_GREEN)
            ax.set_xscale("log")
            ax.set_title("Download size per asset (MB, log scale)")
            ax.set_xlabel("MB")
            ax.set_ylabel("assets")
            created.append(_save(fig, outdir, "sizes_hist.png"))

    vc = stats.get("variant_counts") or {}
    if vc:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(list(vc.keys()), list(vc.values()), color=NVIDIA_GREEN)
        ax.set_title("Physics engine variant coverage")
        ax.set_ylabel("assets")
        created.append(_save(fig, outdir, "variants.png"))

    rates = stats.get("validation_feature_rates") or {}
    if rates:
        items = sorted(rates.items())[::-1]
        fig, ax = plt.subplots(figsize=(8, max(4, 0.32 * len(items))))
        pct = [100 * p / t if t else 0 for _, (p, t) in items]
        ax.barh([k for k, _ in items], pct, color=NVIDIA_GREEN)
        ax.set_xlim(0, 100)
        ax.set_title("Validation pass rate per feature")
        ax.set_xlabel("% of validation rows passing")
        created.append(_save(fig, outdir, "validation.png"))

    growth = stats.get("growth_by_date") or {}
    if growth:
        keys = sorted(growth)
        cumulative = np.cumsum([growth[k] for k in keys])
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(keys, cumulative, marker="o", color=NVIDIA_GREEN)
        ax.set_title("Cumulative assets by packaging date")
        ax.set_ylabel("assets")
        ax.tick_params(axis="x", rotation=45)
        created.append(_save(fig, outdir, "growth.png"))

    return created


def main():
    assets = pd.read_parquet(DATA_DIR / "assets.parquet")
    stats = json.loads((DATA_DIR / "stats.json").read_text(encoding="utf-8"))
    outdir = DATA_DIR.parent / "card" / "assets"
    created = make_charts(assets, stats, outdir)
    logger.info("charts -> %d files in %s", len(created), outdir)


if __name__ == "__main__":
    main()
