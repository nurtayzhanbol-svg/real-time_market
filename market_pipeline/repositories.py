from market_pipeline.models import PricePoint
from market_pipeline.sample_data import SEED_MARKET_DATA


class MarketDataRepository:
    """Read market data from the current backing store."""

    def __init__(self, data: dict[str, list[PricePoint]] | None = None) -> None:
        self._data = data if data is not None else SEED_MARKET_DATA

    def get_price_history(self, ticker: str) -> list[PricePoint] | None:
        normalized_ticker = ticker.upper()
        prices = self._data.get(normalized_ticker)
        if prices is None:
            return None
        return list(prices)

    def list_price_histories(self) -> list[tuple[str, list[PricePoint]]]:
        return [(ticker, list(prices)) for ticker, prices in sorted(self._data.items())]
