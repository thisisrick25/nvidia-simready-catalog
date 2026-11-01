import argparse

import pandas as pd
from huggingface_hub import snapshot_download

from pipeline.config import CACHE_DIR, DATA_DIR, REPO_ID

ALLOW_PATTERNS = [
    "*/simready_usd/payloads/*.usda",
    "*/simready_usd/sm_*.usd",
    "*/com.nvidia.simready.packaging.json",
    "*/.metadata/*",
    "*/.thumbs/256x256/*",
]


def patterns_for_limit(inventory: pd.DataFrame, limit: int) -> list:
    names = sorted(a for a in inventory["asset"].unique() if a != "__root__")
    return [f"{n}/**" for n in names[:limit]]


def fetch(limit=None):
    patterns = list(ALLOW_PATTERNS)
    if limit is not None:
        inv = pd.read_parquet(DATA_DIR / "inventory.parquet")
        patterns = patterns_for_limit(inv, limit)
    path = snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        revision="main",
        local_dir=CACHE_DIR / "simready-assets",
        allow_patterns=patterns,
    )
    return path


def main():
    ap = argparse.ArgumentParser(description="Selectively download SimReady payload files")
    ap.add_argument("--limit", type=int, default=None, help="only first N assets (smoke)")
    ap.add_argument("--dry-run", action="store_true", help="print patterns and exit")
    args = ap.parse_args()
    if args.dry_run:
        if args.limit is not None:
            inv = pd.read_parquet(DATA_DIR / "inventory.parquet")
            print(patterns_for_limit(inv, args.limit))
        else:
            print(ALLOW_PATTERNS)
        return
    path = fetch(limit=args.limit)
    print(f"fetched to {path}")


if __name__ == "__main__":
    main()
