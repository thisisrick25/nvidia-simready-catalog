import argparse
import logging
import os
import sys

from huggingface_hub import HfApi, get_token

from pipeline.config import CARD_DIR, DATA_DIR, ROOT

logger = logging.getLogger(__name__)

DEFAULT_NAMESPACE = os.environ.get(
    "SIMREADY_HF_NAMESPACE", "thisisrick25"
)


def require_token():
    token = os.environ.get("HF_TOKEN") or get_token()
    if not token:
        sys.exit(
            "No HuggingFace token found. "
            "Set HF_TOKEN or run `huggingface-cli login`."
        )
    return token


def publish_dataset(namespace: str, api: HfApi) -> str:
    repo_id = f"{namespace}/nvidia-simready-catalog"
    logger.info("publishing dataset to %s", repo_id)
    api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
    api.upload_file(
        path_or_fileobj=str(CARD_DIR / "README.md"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset",
    )
    api.upload_folder(
        folder_path=str(DATA_DIR),
        repo_id=repo_id,
        repo_type="dataset",
        allow_patterns=["*.parquet", "stats.json"],
    )
    logger.info("dataset published: %s", repo_id)
    return repo_id


def publish_space(namespace: str, api: HfApi) -> str:
    repo_id = f"{namespace}/nvidia-simready-catalog"
    logger.info("publishing space to %s", repo_id)
    api.create_repo(
        repo_id,
        repo_type="space",
        space_sdk="gradio",
        exist_ok=True,
    )
    api.upload_folder(
        folder_path=str(ROOT / "portal"),
        repo_id=repo_id,
        repo_type="space",
    )
    logger.info("space published: %s", repo_id)
    return repo_id


def main():
    parser = argparse.ArgumentParser(description="Publish to HuggingFace")
    parser.add_argument(
        "--namespace", default=DEFAULT_NAMESPACE,
        help="HF namespace (default: %(default)s)",
    )
    parser.add_argument(
        "--what", choices=["dataset", "space", "both"], default="both",
        help="What to publish (default: %(default)s)",
    )
    args = parser.parse_args()

    token = require_token()
    api = HfApi(token=token)

    if args.what in ("dataset", "both"):
        publish_dataset(args.namespace, api)
    if args.what in ("space", "both"):
        publish_space(args.namespace, api)


if __name__ == "__main__":
    main()
