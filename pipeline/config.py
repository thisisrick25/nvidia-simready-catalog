import os
from pathlib import Path

REPO_ID = os.environ.get("SIMREADY_REPO_ID", "nvidia/simready-assets")
REPO_TYPE = "dataset"
REVISION = os.environ.get("SIMREADY_REVISION", "main")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("SIMREADY_DATA_DIR", ROOT / "data"))
CACHE_DIR = Path(os.environ.get("SIMREADY_CACHE_DIR", DATA_DIR / "cache"))
CARD_DIR = ROOT / "card"
PORTAL_DATA_DIR = ROOT / "portal" / "data"
PORTAL_STATIC_DATA_DIR = ROOT / "portal" / "public" / "data"

HF_BASE = f"https://huggingface.co/datasets/{REPO_ID}/resolve/main/"
