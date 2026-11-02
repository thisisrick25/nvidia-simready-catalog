import logging
from pathlib import Path

import pandas as pd

from pipeline.config import DATA_DIR
from pipeline.hf_client import iter_repo_files

logger = logging.getLogger(__name__)


def asset_of(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else "__root__"


def classify(path: str) -> str:
    p = path.lower()
    base = p.rsplit("/", 1)[-1]
    if "/.metadata/" in p:
        return "metadata"
    if base == "com.nvidia.simready.packaging.json":
        return "packaging_json"
    if "/simready_usd/payloads/" in p:
        if base == "geometries.usd":
            return "geometry"
        if base.endswith(".usda"):
            return "payload_usda"
        return "payload_usd_other"
    if "/simready_usd/" in p and base.startswith("sm_") and base.endswith(".usd"):
        return "sm_usd"
    if "/.thumbs/" in p:
        # Real NVIDIA thumbnail filenames (verified against production data):
        # sm_<name>.usd.png (default render), sm_<name>.usd_light.png,
        # sm_<name>.usd_transparent.png, sm_<name>_thumbnail.png (composite).
        # None of these contain the word "lit"/"unlit" - that distinction
        # does not exist in the real dataset.
        if base.endswith("_thumbnail.png"):
            return "thumb_composite"
        if base.endswith(".usd_light.png"):
            return "thumb_light"
        if base.endswith(".usd_transparent.png"):
            return "thumb_transparent"
        if base.endswith(".usd.png"):
            return "thumb_default"
        if base.endswith(".png"):
            return "thumb_other"
        return "thumb_other"
    if "/textures/" in p:
        return "texture"
    if "/source_assets/" in p:
        return "source_asset"
    if "/payloads/" in p:
        return "payload_other"
    return "other"


def build_inventory(records) -> pd.DataFrame:
    rows = [
        {
            "path": r["path"],
            "asset": asset_of(r["path"]),
            "size": int(r["size"] or 0),
            "kind": classify(r["path"]),
            "ext": Path(r["path"]).suffix,
        }
        for r in records
    ]
    df = pd.DataFrame(rows, columns=["path", "asset", "size", "kind", "ext"])
    return df.sort_values("path").reset_index(drop=True)


def main():
    df = build_inventory(iter_repo_files())
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / "inventory.parquet"
    df.to_parquet(out)
    n_assets = df.loc[df["asset"] != "__root__", "asset"].nunique()
    logger.info("inventory: %d files, %d assets, %.2f GB -> %s", len(df), n_assets, df["size"].sum() / 1e9, out)


if __name__ == "__main__":
    main()
