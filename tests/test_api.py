from collections.abc import AsyncIterator

import httpx
import pytest

from market_pipeline.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.mark.anyio
async def test_health_check(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_get_latest_price(client: httpx.AsyncClient) -> None:
    response = await client.get("/prices/latest/aapl")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "AAPL"
    assert payload["price"] == 198.1


@pytest.mark.anyio
async def test_get_price_history(client: httpx.AsyncClient) -> None:
    response = await client.get("/prices/history/MSFT")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 5
    assert payload[0]["ticker"] == "MSFT"


@pytest.mark.anyio
async def test_get_metrics(client: httpx.AsyncClient) -> None:
    response = await client.get("/metrics/BTC-USD")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "BTC-USD"
    assert payload["moving_average_3"] == 119190.0
    assert payload["latest_return_percent"] == 0.461
    assert payload["price_change_percent"] == 1.3531


@pytest.mark.anyio
async def test_get_market_summary(client: httpx.AsyncClient) -> None:
    response = await client.get("/market/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["tickers"] == 3
    assert payload["total_volume"] > 0
    assert {item["ticker"] for item in payload["items"]} == {"AAPL", "BTC-USD", "MSFT"}


@pytest.mark.anyio
async def test_unknown_ticker_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.get("/prices/latest/UNKNOWN")

    assert response.status_code == 404
