import pandas as pd
import pytest

from pipeline import fetch
from pipeline.fetch import ALLOW_PATTERNS, patterns_for_limit


def _inv():
    return pd.DataFrame(
        {"asset": ["a_asset_x01", "b_asset_y02", "c_asset_z03"], "kind": ["packaging_json"] * 3}
    )


def test_default_patterns_cover_needed_files():
    joined = " ".join(ALLOW_PATTERNS)
    for needle in ("payloads/*.usda", "sm_*.usd", "com.nvidia.simready.packaging.json", ".metadata/", ".thumbs/256x256/"):
        assert needle in joined


def test_patterns_for_limit():
    pats = patterns_for_limit(_inv(), 2)
    assert pats == ["a_asset_x01/**", "b_asset_y02/**"]
    assert patterns_for_limit(_inv(), 10) == ["a_asset_x01/**", "b_asset_y02/**", "c_asset_z03/**"]


def test_fetch_retries_transient_hub_failure(monkeypatch):
    calls = []

    def download(**kwargs):
        calls.append(kwargs)
        if len(calls) < 3:
            raise fetch.LocalEntryNotFoundError("temporary failure")
        return "downloaded"

    monkeypatch.setattr(fetch, "snapshot_download", download)
    monkeypatch.setattr(fetch.time, "sleep", lambda _: None)

    assert fetch.fetch() == "downloaded"
    assert len(calls) == 3


def test_fetch_raises_after_retry_limit(monkeypatch):
    calls = []
    error = fetch.LocalEntryNotFoundError("persistent failure")

    def download(**kwargs):
        calls.append(kwargs)
        raise error

    monkeypatch.setattr(fetch, "snapshot_download", download)
    monkeypatch.setattr(fetch.time, "sleep", lambda _: None)

    with pytest.raises(fetch.LocalEntryNotFoundError, match="persistent failure"):
        fetch.fetch()
    assert len(calls) == fetch.DOWNLOAD_ATTEMPTS
