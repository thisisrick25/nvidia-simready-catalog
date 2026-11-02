from unittest.mock import patch, MagicMock

from pipeline.run_all import main


@patch("pipeline.run_all.sync_portal_data")
@patch("pipeline.run_all.build_card")
@patch("pipeline.run_all.charts")
@patch("pipeline.run_all.aggregate")
@patch("pipeline.run_all.extract")
@patch("pipeline.run_all.fetch")
@patch("pipeline.run_all.inventory")
@patch("sys.argv", ["run_all", "--skip-fetch"])
def test_main_calls_all_stages_skip_fetch(
    mock_inv, mock_fetch, mock_extract, mock_agg, mock_charts, mock_card, mock_sync
):
    mock_agg.main.return_value = {
        "n_assets": 10,
        "n_categories": 3,
        "as_of": "2026-01-01",
    }
    main()
    mock_inv.main.assert_called_once()
    mock_fetch.fetch.assert_not_called()
    mock_extract.main.assert_called_once()
    mock_agg.main.assert_called_once()
    mock_charts.main.assert_called_once()
    mock_card.main.assert_called_once()
    mock_sync.assert_called_once()


@patch("pipeline.run_all.sync_portal_data")
@patch("pipeline.run_all.build_card")
@patch("pipeline.run_all.charts")
@patch("pipeline.run_all.aggregate")
@patch("pipeline.run_all.extract")
@patch("pipeline.run_all.fetch")
@patch("pipeline.run_all.inventory")
@patch("sys.argv", ["run_all"])
def test_main_runs_fetch_by_default(
    mock_inv, mock_fetch, mock_extract, mock_agg, mock_charts, mock_card, mock_sync
):
    mock_agg.main.return_value = {
        "n_assets": 5,
        "n_categories": 2,
        "as_of": "2026-01-01",
    }
    main()
    mock_fetch.fetch.assert_called_once()
