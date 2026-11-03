import argparse
import logging
import sys
import time

import pandas as pd
from huggingface_hub import snapshot_download
from huggingface_hub.errors import HfHubHTTPError, LocalEntryNotFoundError

from pipeline.config import CACHE_DIR, DATA_DIR, REPO_ID

logger = logging.getLogger(__name__)

DOWNLOAD_ATTEMPTS = 10
RETRY_DELAY_SECONDS = 10
DOWNLOAD_WORKERS = 4

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
        inv_path = DATA_DIR / "inventory.parquet"
        if not inv_path.exists():
            sys.exit("Run 'python -m pipeline.inventory' first, or run without --limit")
        inv = pd.read_parquet(inv_path)
        patterns = patterns_for_limit(inv, limit)
    for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
        try:
            return snapshot_download(
                repo_id=REPO_ID,
                repo_type="dataset",
                revision="main",
                local_dir=CACHE_DIR / "simready-assets",
                allow_patterns=patterns,
                max_workers=DOWNLOAD_WORKERS,
            )
        except (HfHubHTTPError, LocalEntryNotFoundError) as exc:
            if attempt == DOWNLOAD_ATTEMPTS:
                logger.error("Hugging Face download failed after %d attempts", attempt)
                raise
            delay = RETRY_DELAY_SECONDS * attempt
            logger.warning(
                "Hugging Face download attempt %d/%d failed: %s; retrying in %d seconds",
                attempt,
                DOWNLOAD_ATTEMPTS,
                exc,
                delay,
            )
            time.sleep(delay)


def main():
    ap = argparse.ArgumentParser(
        description="Selectively download SimReady payload files"
    )
    ap.add_argument(
        "--limit", type=int, default=None, help="only first N assets (smoke)"
    )
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
    logger.info("fetched to %s", path)


if __name__ == "__main__":
    main()
