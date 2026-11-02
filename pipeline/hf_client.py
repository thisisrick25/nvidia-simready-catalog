import logging
from typing import Iterator

from huggingface_hub import HfApi
from huggingface_hub.hf_api import RepoFile

from pipeline.config import REPO_ID, REPO_TYPE, REVISION

logger = logging.getLogger(__name__)
_api = HfApi()


def iter_repo_files(repo_id: str = REPO_ID) -> Iterator[dict]:
    """Yield {"path", "size"} for every file in the dataset repo."""
    for item in _api.list_repo_tree(
        repo_id, repo_type=REPO_TYPE, revision=REVISION, recursive=True
    ):
        if isinstance(item, RepoFile):
            yield {"path": item.path, "size": item.size or 0}
