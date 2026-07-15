from datetime import datetime

from pydantic import BaseModel, Field


class PricePoint(BaseModel):
    ticker: str = Field(..., examples=["AAPL"])
    timestamp: datetime
    price: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)


class LatestPrice(BaseModel):
    ticker: str
    timestamp: datetime
    price: float
    volume: int


class Metrics(BaseModel):
    ticker: str
    latest_price: float
    moving_average_3: float
    moving_average_5: float
    latest_return_percent: float
    volatility_percent: float
    vwap: float
    price_change_percent: float


class MarketSummaryItem(BaseModel):
    ticker: str
    latest_price: float
    price_change_percent: float
    volume: int


class MarketSummary(BaseModel):
    tickers: int
    total_volume: int
    items: list[MarketSummaryItem]
