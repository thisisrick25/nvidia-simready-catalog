import pytest

from pipeline.parse_usdc import HAS_PXR, parse_sm_usd


def test_guarded_import():
    assert isinstance(HAS_PXR, bool)


@pytest.mark.skipif(not HAS_PXR, reason="usd-core not installed")
def test_parse_missing_file_returns_none(tmp_path):
    assert parse_sm_usd(tmp_path / "nope.usd") is None


@pytest.mark.skipif(HAS_PXR, reason="pxr installed; None-return path for missing pxr")
def test_returns_none_without_pxr(tmp_path):
    assert parse_sm_usd(tmp_path / "nope.usd") is None