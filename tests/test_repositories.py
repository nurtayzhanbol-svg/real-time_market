from datetime import datetime, timezone

from market_pipeline.models import PricePoint
from market_pipeline.repositories import MarketDataRepository
from market_pipeline.sample_data import SAMPLE_MARKET_DATA, SEED_MARKET_DATA


def test_default_repository_uses_seed_data() -> None:
    repository = MarketDataRepository()

    prices = repository.get_price_history("AAPL")

    assert prices is not None
    assert prices == SEED_MARKET_DATA["AAPL"]


def test_sample_market_data_alias_points_to_seed_data() -> None:
    assert SAMPLE_MARKET_DATA is SEED_MARKET_DATA


def test_get_price_history_normalizes_ticker() -> None:
    repository = MarketDataRepository(
        {
            "AAPL": [
                PricePoint(
                    ticker="AAPL",
                    timestamp=datetime(2026, 7, 12, 9, 30, tzinfo=timezone.utc),
                    price=195.12,
                    volume=1250,
                )
            ]
        }
    )

    prices = repository.get_price_history("aapl")

    assert prices is not None
    assert prices[0].ticker == "AAPL"


def test_get_price_history_returns_none_for_unknown_ticker() -> None:
    repository = MarketDataRepository({})

    assert repository.get_price_history("UNKNOWN") is None


def test_list_price_histories_returns_sorted_tickers() -> None:
    repository = MarketDataRepository(
        {
            "MSFT": [],
            "AAPL": [],
        }
    )

    assert [ticker for ticker, _ in repository.list_price_histories()] == ["AAPL", "MSFT"]
