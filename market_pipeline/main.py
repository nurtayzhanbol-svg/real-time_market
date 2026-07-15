from fastapi import FastAPI, HTTPException

from market_pipeline.models import LatestPrice, MarketSummary, Metrics, PricePoint
from market_pipeline.services import MarketDataService, TickerNotFoundError

app = FastAPI(
    title="Real-Time Market Data Pipeline",
    version="0.1.0",
    description="Simple skeleton API for market prices and analytics.",
)

market_data_service = MarketDataService()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/prices/latest/{ticker}", response_model=LatestPrice)
async def get_latest_price(ticker: str) -> LatestPrice:
    try:
        return market_data_service.latest_price(ticker)
    except TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/prices/history/{ticker}", response_model=list[PricePoint])
async def get_price_history(ticker: str) -> list[PricePoint]:
    try:
        return market_data_service.price_history(ticker)
    except TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/metrics/{ticker}", response_model=Metrics)
async def get_metrics(ticker: str) -> Metrics:
    try:
        return market_data_service.metrics(ticker)
    except TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/market/summary", response_model=MarketSummary)
async def get_market_summary() -> MarketSummary:
    return market_data_service.market_summary()
