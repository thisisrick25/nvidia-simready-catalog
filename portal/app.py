import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"


st.set_page_config(page_title="SimReady Assets Explorer", page_icon="🤖", layout="wide")


@st.cache_data
def load(name):
    return pd.read_parquet(DATA / f"{name}.parquet")


assets = load("assets")
validation = load("validation")
stats = json.loads((DATA / "stats.json").read_text(encoding="utf-8"))

st.title("SimReady Assets Explorer")
st.caption(
    f"Community catalog of [nvidia/simready-assets]("
    f"https://huggingface.co/datasets/nvidia/simready-assets) — "
    f"data as of {stats.get('as_of', 'unknown')}"
)

c1, c2, c3, c4, c5 = st.columns(5)
vc = stats.get("variant_counts") or {}
c1.metric("Assets", f"{len(assets):,}")
c2.metric("Total size", f"{stats.get('total_size_gb', 'n/a')} GB")
c3.metric("Categories", str(stats.get("n_categories", "n/a")))
c4.metric(
    "Articulated",
    f"{stats.get('articulated_count', 0):,} ({stats.get('articulated_pct', 0)}%)",
)
c5.metric(
    "PhysX / MuJoCo / Newton",
    f"{vc.get('PhysX', 0):,} / {vc.get('MuJoCo', 0):,} / {vc.get('Newton', 0):,}",
)

tab_overview, tab_assets, tab_validation, tab_about = st.tabs(
    ["Overview", "Assets", "Validation", "About"]
)

with tab_overview:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Assets per category (top 20)")
        cats = pd.Series(stats.get("category_counts") or {}).sort_values(
            ascending=False
        )
        if len(cats):
            st.bar_chart(cats.head(20))
    with col2:
        st.subheader("Mass distribution (kg, log bins)")
        mass = pd.to_numeric(assets["mass_kg"], errors="coerce").dropna()
        if len(mass):
            lo = max(float(mass.min()), 1e-4)
            bins = np.logspace(np.log10(lo), np.log10(float(mass.max()) * 1.01), 30)
            hist, edges = np.histogram(mass, bins=bins)
            st.bar_chart(
                pd.Series(hist, index=[f"{e:.3g}" for e in edges[:-1]])
            )
    st.subheader("Physics engine variant coverage")
    if vc:
        st.bar_chart(pd.Series(vc))
    st.subheader("Cumulative assets by packaging date")
    growth = pd.Series(stats.get("growth_by_date") or {})
    if len(growth):
        st.line_chart(growth.sort_index().cumsum())

with tab_assets:
    groups = sorted(assets["taxonomy_group"].dropna().unique().tolist())
    cat_filter = st.multiselect("Category", groups)
    q = st.text_input("Search asset name")
    view = assets
    if cat_filter:
        view = view[view["taxonomy_group"].isin(cat_filter)]
    if q:
        view = view[view["asset"].str.contains(q, case=False, na=False)]
    st.write(f"{len(view)} assets")
    display = view[
        [
            "asset",
            "asset_type",
            "taxonomy_group",
            "mass_kg",
            "rigid_body_count",
            "has_articulation",
            "features_passed",
            "features_total",
            "size_total_bytes",
            "thumb_url",
        ]
    ].rename(columns={"thumb_url": "thumbnail"})
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "mass_kg": st.column_config.NumberColumn(format="%.3g"),
            "size_total_bytes": st.column_config.NumberColumn("size (B)", format="%d"),
            "thumbnail": st.column_config.ImageColumn("thumbnail"),
        },
    )

with tab_validation:
    st.subheader("Pass rate per feature")
    rates = stats.get("validation_feature_rates") or {}
    if rates:
        rows = [
            {"feature": k, "pass rate": f"{100 * p / t:.1f}%", "passed": p, "total": t}
            for k, (p, t) in sorted(rates.items())
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.subheader("Assets with failing features")
    fail_assets = assets[assets["all_features_passed"] == False]["asset"].tolist()
    st.write(f"{len(fail_assets)} of {len(assets)} assets have at least one failing feature")
    sel = st.selectbox("Inspect asset", fail_assets)
    if sel:
        st.dataframe(
            validation[validation["asset"] == sel].drop(columns=["asset"]),
            hide_index=True,
            use_container_width=True,
        )

with tab_about:
    st.markdown(
        """
This portal is a community project; the underlying assets are © NVIDIA Corporation,
licensed [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
Credit: NVIDIA SimReady Assets — https://huggingface.co/datasets/nvidia/simready-assets.

- Data catalog and pipeline: see the companion dataset page for per-asset tables
- Validation terminology: [simready-foundation](https://github.com/NVIDIA/simready-foundation)
- Assets referenced via hotlinked thumbnails served from the HF dataset
"""
    )