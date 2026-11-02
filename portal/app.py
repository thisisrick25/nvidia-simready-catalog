import json
from pathlib import Path

import gradio as gr
import numpy as np
import pandas as pd

DATA = Path(__file__).parent / "data"


def load(name):
    return pd.read_parquet(DATA / f"{name}.parquet")


def load_stats():
    return json.loads((DATA / "stats.json").read_text(encoding="utf-8"))


assets = load("assets")
validation = load("validation")
stats = load_stats()

vc = stats.get("variant_counts") or {}
metrics_md = (
    f"**Assets:** {len(assets):,} · "
    f"**Total size:** {stats.get('total_size_gb', 'n/a')} GB · "
    f"**Categories:** {stats.get('n_categories', 'n/a')} · "
    f"**Articulated:** {stats.get('articulated_count', 0):,} "
    f"({stats.get('articulated_pct', 0)}%) · "
    f"**PhysX / MuJoCo / Newton:** "
    f"{vc.get('PhysX', 0):,} / {vc.get('MuJoCo', 0):,} / {vc.get('Newton', 0):,}"
)


def build_category_chart():
    cats = pd.Series(stats.get("category_counts") or {}).sort_values(ascending=True)
    cats = cats.tail(20)
    return gr.BarPlot(
        pd.DataFrame({"category": cats.index, "count": cats.values}),
        x="count",
        y="category",
        x_title="Count",
        y_title="",
        title="Assets per category (top 20)",
    )


def build_variant_chart():
    if not vc:
        return gr.BarPlot(pd.DataFrame({"variant": [], "count": []}), x="variant", y="count")
    return gr.BarPlot(
        pd.DataFrame({"variant": list(vc.keys()), "count": list(vc.values())}),
        x="variant",
        y="count",
        title="Physics engine variant coverage",
    )


def build_growth_chart():
    growth = pd.Series(stats.get("growth_by_date") or {})
    if growth.empty:
        return gr.LinePlot(pd.DataFrame({"date": [], "assets": []}), x="date", y="assets")
    cumulative = growth.sort_index().cumsum()
    return gr.LinePlot(
        pd.DataFrame({"date": cumulative.index, "assets": cumulative.values}),
        x="date",
        y="assets",
        title="Cumulative assets by packaging date",
    )


def build_mass_histogram():
    mass = pd.to_numeric(assets["mass_kg"], errors="coerce").dropna()
    mass = mass[mass > 0]
    if mass.empty:
        return gr.BarPlot(pd.DataFrame({"bin": [], "count": []}), x="bin", y="count")
    lo = float(mass.min())
    bins = np.logspace(np.log10(lo), np.log10(float(mass.max()) * 1.01), 30)
    hist, edges = np.histogram(mass, bins=bins)
    return gr.BarPlot(
        pd.DataFrame({"bin": [f"{e:.3g}" for e in edges[:-1]], "count": hist}),
        x="bin",
        y="count",
        title="Mass distribution (kg, log bins)",
    )


DISPLAY_COLUMNS = [
    "asset",
    "asset_type",
    "taxonomy_group",
    "mass_kg",
    "rigid_body_count",
    "has_articulation",
    "features_passed",
    "features_total",
    "size_total_bytes",
]

groups = sorted(assets["taxonomy_group"].dropna().unique().tolist())


def filter_assets(categories, query):
    view = assets
    if categories:
        view = view[view["taxonomy_group"].isin(categories)]
    if query:
        view = view[view["asset"].str.contains(query, case=False, na=False, regex=False)]
    display = view[DISPLAY_COLUMNS].copy()
    display["mass_kg"] = display["mass_kg"].apply(lambda x: f"{x:.3g}" if pd.notna(x) else "")
    display["size_total_bytes"] = display["size_total_bytes"].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else ""
    )
    display = display.rename(columns={"size_total_bytes": "size (B)"})
    return gr.Dataframe(value=display, label=f"{len(view)} assets")


def get_fail_assets():
    return assets[assets["all_features_passed"].eq(False)]["asset"].tolist()


fail_list = get_fail_assets()


def inspect_asset(selected):
    if not selected:
        return pd.DataFrame()
    return validation[validation["asset"] == selected].drop(columns=["asset"])


with gr.Blocks(title="SimReady Assets Explorer") as demo:
    gr.Markdown(
        f"# SimReady Assets Explorer\n"
        f"Community catalog of [nvidia/simready-assets]"
        f"(https://huggingface.co/datasets/nvidia/simready-assets) — "
        f"data as of {stats.get('as_of', 'unknown')}"
    )
    gr.Markdown(metrics_md)

    with gr.Tab("Overview"):
        with gr.Row():
            build_category_chart()
            build_mass_histogram()
        with gr.Row():
            build_variant_chart()
            build_growth_chart()

    with gr.Tab("Assets"):
        with gr.Row():
            cat_filter = gr.Dropdown(
                choices=groups, multiselect=True, label="Category", interactive=True
            )
            search_box = gr.Textbox(label="Search asset name", interactive=True)
        asset_table = gr.Dataframe(
            value=assets[DISPLAY_COLUMNS].rename(columns={"size_total_bytes": "size (B)"}),
            label=f"{len(assets)} assets",
            interactive=False,
        )
        cat_filter.change(filter_assets, inputs=[cat_filter, search_box], outputs=asset_table)
        search_box.submit(filter_assets, inputs=[cat_filter, search_box], outputs=asset_table)

    with gr.Tab("Validation"):
        gr.Markdown("### Pass rate per feature")
        rates = stats.get("validation_feature_rates") or {}
        if rates:
            rows = [
                {"feature": k, "pass rate": f"{100 * p / t:.1f}%", "passed": p, "total": t}
                for k, (p, t) in sorted(rates.items())
            ]
            gr.Dataframe(value=pd.DataFrame(rows), interactive=False)
        gr.Markdown(
            f"### Assets with failing features\n"
            f"{len(fail_list)} of {len(assets)} assets have at least one failing feature"
        )
        asset_selector = gr.Dropdown(
            choices=fail_list, label="Inspect asset", interactive=True
        )
        detail_table = gr.Dataframe(interactive=False)
        asset_selector.change(inspect_asset, inputs=asset_selector, outputs=detail_table)

    with gr.Tab("About"):
        gr.Markdown(
            """
This portal is a community project; the underlying assets are © NVIDIA Corporation,
licensed [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
Credit: NVIDIA SimReady Assets — https://huggingface.co/datasets/nvidia/simready-assets.

- Data catalog and pipeline: see the companion dataset page for per-asset tables
- Validation terminology: [simready-foundation](https://github.com/NVIDIA/simready-foundation)
- Assets referenced via hotlinked thumbnails served from the HF dataset
"""
        )

if __name__ == "__main__":
    demo.launch()
