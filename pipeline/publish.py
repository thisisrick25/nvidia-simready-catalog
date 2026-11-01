import argparse
import os

from huggingface_hub import HfApi, get_token

from pipeline.config import CARD_DIR, DATA_DIR, ROOT


def require_token():
    token = os.environ.get("HF_TOKEN") or get_token()
    if not token:
        raise SystemExit(
            "No HF token. Create a write token at "
            "https://huggingface.co/settings/tokens and set $env:HF_TOKEN."
        )
    return token


def publish_dataset(namespace, api):
    repo_id = f"{namespace}/simready-assets-catalog"
    api.create_repo(repo_id, repo_type="dataset", private=False, exist_ok=True)
    api.upload_file(
        path_or_fileobj=str(CARD_DIR / "README.md"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset",
    )
    api.upload_folder(
        folder_path=str(DATA_DIR),
        path_in_repo="data",
        repo_id=repo_id,
        repo_type="dataset",
        allow_patterns=["*.parquet", "stats.json"],
    )
    print(f"dataset -> https://huggingface.co/datasets/{repo_id}")


def publish_space(namespace, api):
    repo_id = f"{namespace}/simready-assets-portal"
    api.create_repo(
        repo_id,
        repo_type="space",
        space_sdk="streamlit",
        private=False,
        exist_ok=True,
    )
    api.upload_folder(
        folder_path=str(ROOT / "portal"),
        path_in_repo=".",
        repo_id=repo_id,
        repo_type="space",
    )
    print(f"space -> https://huggingface.co/spaces/{repo_id}")


def main():
    ap = argparse.ArgumentParser(description="Publish catalog dataset and portal Space")
    ap.add_argument("--namespace", required=True, help="your Hugging Face username")
    ap.add_argument(
        "--what", choices=["dataset", "space", "both"], default="both"
    )
    args = ap.parse_args()
    api = HfApi(token=require_token())
    if args.what in ("dataset", "both"):
        publish_dataset(args.namespace, api)
    if args.what in ("space", "both"):
        publish_space(args.namespace, api)


if __name__ == "__main__":
    main()
