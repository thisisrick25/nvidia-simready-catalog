from pathlib import Path

REPO_ID = "nvidia/simready-assets"
REPO_TYPE = "dataset"
REVISION = "main"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
CARD_DIR = ROOT / "card"

HF_BASE = f"https://huggingface.co/datasets/{REPO_ID}/resolve/main/"
