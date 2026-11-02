from unittest.mock import patch, MagicMock

from huggingface_hub.hf_api import RepoFile, RepoFolder

from pipeline.hf_client import iter_repo_files


def test_iter_repo_files_yields_files_only():
    file1 = MagicMock(spec=RepoFile)
    file1.path = "asset_a/sm.usd"
    file1.size = 1234

    file2 = MagicMock(spec=RepoFile)
    file2.path = "asset_b/sm.usd"
    file2.size = 0

    folder = MagicMock(spec=RepoFolder)
    folder.path = "asset_a"

    with patch("pipeline.hf_client._api") as mock_api:
        mock_api.list_repo_tree.return_value = [file1, folder, file2]
        result = list(iter_repo_files("test/repo"))

    assert len(result) == 2
    assert result[0] == {"path": "asset_a/sm.usd", "size": 1234}
    assert result[1] == {"path": "asset_b/sm.usd", "size": 0}
