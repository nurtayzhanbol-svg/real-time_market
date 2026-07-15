from statistics import pstdev

from market_pipeline.models import (
    LatestPrice,
    MarketSummary,
    MarketSummaryItem,
    Metrics,
    PricePoint,
)
from market_pipeline.repositories import MarketDataRepository


class TickerNotFoundError(ValueError):
    """Raised when a requested ticker is not available."""


class MarketDataService:
    def __init__(
        self,
        repository: MarketDataRepository | None = None,
        data: dict[str, list[PricePoint]] | None = None,
    ) -> None:
        if repository is not None and data is not None:
            raise ValueError("Provide either repository or data, not both")
        self._repository = repository or MarketDataRepository(data or None)

    def latest_price(self, ticker: str) -> LatestPrice:
        prices = self.price_history(ticker)
        latest = prices[-1]
        return LatestPrice(
            ticker=latest.ticker,
            timestamp=latest.timestamp,
            price=latest.price,
            volume=latest.volume,
        )

    def price_history(self, ticker: str) -> list[PricePoint]:
        prices = self._repository.get_price_history(ticker)
        if not prices:
            raise TickerNotFoundError(f"Ticker '{ticker}' was not found")
        return prices

    def metrics(self, ticker: str) -> Metrics:
        prices = self.price_history(ticker)
        latest = prices[-1]
        returns = self._returns(prices)

        return Metrics(
            ticker=latest.ticker,
            latest_price=latest.price,
            moving_average_3=self._moving_average(prices, window=3),
            moving_average_5=self._moving_average(prices, window=5),
            latest_return_percent=round(returns[-1], 4) if returns else 0.0,
            volatility_percent=round(pstdev(returns), 4) if len(returns) > 1 else 0.0,
            vwap=self._vwap(prices),
            price_change_percent=self._price_change_percent(prices),
        )

    def market_summary(self) -> MarketSummary:
        items = [
            MarketSummaryItem(
                ticker=ticker,
                latest_price=self.latest_price(ticker).price,
                price_change_percent=self._price_change_percent(prices),
                volume=sum(price.volume for price in prices),
            )
            for ticker, prices in self._repository.list_price_histories()
        ]

        return MarketSummary(
            tickers=len(items),
            total_volume=sum(item.volume for item in items),
            items=items,
        )

    @staticmethod
    def _moving_average(prices: list[PricePoint], window: int) -> float:
        window_prices = prices[-window:]
        return round(sum(point.price for point in window_prices) / len(window_prices), 4)

    @staticmethod
    def _returns(prices: list[PricePoint]) -> list[float]:
        returns: list[float] = []
        for previous, current in zip(prices, prices[1:]):
            returns.append(((current.price - previous.price) / previous.price) * 100)
        return returns

    @staticmethod
    def _vwap(prices: list[PricePoint]) -> float:
        total_volume = sum(point.volume for point in prices)
        if total_volume == 0:
            return 0.0
        traded_value = sum(point.price * point.volume for point in prices)
        return round(traded_value / total_volume, 4)

    @staticmethod
    def _price_change_percent(prices: list[PricePoint]) -> float:
        first = prices[0].price
        latest = prices[-1].price
        return round(((latest - first) / first) * 100, 4)
