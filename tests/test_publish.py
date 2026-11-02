from unittest.mock import MagicMock, patch

from huggingface_hub import SpaceHardware

from pipeline.publish import publish_dataset, publish_space, require_token


def test_publish_dataset_creates_repo_and_uploads():
    api = MagicMock()
    result = publish_dataset("myns", api)
    assert result == "myns/nvidia-simready-catalog"
    api.create_repo.assert_called_once_with(
        "myns/nvidia-simready-catalog", repo_type="dataset", exist_ok=True,
    )
    api.upload_file.assert_called_once()
    api.upload_folder.assert_called_once()
    call_kw = api.upload_folder.call_args
    assert call_kw.kwargs["repo_type"] == "dataset"
    assert "*.parquet" in call_kw.kwargs["allow_patterns"]


def test_publish_space_creates_repo_and_uploads():
    api = MagicMock()
    result = publish_space("myns", api)
    assert result == "myns/nvidia-simready-catalog"
    api.create_repo.assert_called_once_with(
        "myns/nvidia-simready-catalog",
        repo_type="space",
        space_sdk="gradio",
        space_hardware=SpaceHardware.CPU_BASIC,
        exist_ok=True,
    )
    api.upload_folder.assert_called_once()
    call_kw = api.upload_folder.call_args
    assert call_kw.kwargs["repo_type"] == "space"


@patch.dict("os.environ", {"HF_TOKEN": "test-token"})
def test_require_token_from_env():
    assert require_token() == "test-token"


@patch.dict("os.environ", {}, clear=True)
@patch("pipeline.publish.get_token", return_value=None)
def test_require_token_exits_when_missing(mock_get):
    import pytest
    with pytest.raises(SystemExit):
        require_token()
