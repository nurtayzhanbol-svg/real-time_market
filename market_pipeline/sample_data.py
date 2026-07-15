from datetime import datetime, timezone

from market_pipeline.models import PricePoint


SAMPLE_MARKET_DATA: dict[str, list[PricePoint]] = {
    "AAPL": [
        PricePoint(
            ticker="AAPL",
            timestamp=datetime(2026, 7, 12, 9, 30, tzinfo=timezone.utc),
            price=195.12,
            volume=1250,
        ),
        PricePoint(
            ticker="AAPL",
            timestamp=datetime(2026, 7, 12, 10, 0, tzinfo=timezone.utc),
            price=196.03,
            volume=2100,
        ),
        PricePoint(
            ticker="AAPL",
            timestamp=datetime(2026, 7, 12, 10, 30, tzinfo=timezone.utc),
            price=195.64,
            volume=1840,
        ),
        PricePoint(
            ticker="AAPL",
            timestamp=datetime(2026, 7, 12, 11, 0, tzinfo=timezone.utc),
            price=197.25,
            volume=2600,
        ),
        PricePoint(
            ticker="AAPL",
            timestamp=datetime(2026, 7, 12, 11, 30, tzinfo=timezone.utc),
            price=198.1,
            volume=2300,
        ),
    ],
    "MSFT": [
        PricePoint(
            ticker="MSFT",
            timestamp=datetime(2026, 7, 12, 9, 30, tzinfo=timezone.utc),
            price=511.45,
            volume=980,
        ),
        PricePoint(
            ticker="MSFT",
            timestamp=datetime(2026, 7, 12, 10, 0, tzinfo=timezone.utc),
            price=512.2,
            volume=1210,
        ),
        PricePoint(
            ticker="MSFT",
            timestamp=datetime(2026, 7, 12, 10, 30, tzinfo=timezone.utc),
            price=509.9,
            volume=1680,
        ),
        PricePoint(
            ticker="MSFT",
            timestamp=datetime(2026, 7, 12, 11, 0, tzinfo=timezone.utc),
            price=514.8,
            volume=1900,
        ),
        PricePoint(
            ticker="MSFT",
            timestamp=datetime(2026, 7, 12, 11, 30, tzinfo=timezone.utc),
            price=516.35,
            volume=1750,
        ),
    ],
    "BTC-USD": [
        PricePoint(
            ticker="BTC-USD",
            timestamp=datetime(2026, 7, 12, 9, 30, tzinfo=timezone.utc),
            price=118250.0,
            volume=12,
        ),
        PricePoint(
            ticker="BTC-USD",
            timestamp=datetime(2026, 7, 12, 10, 0, tzinfo=timezone.utc),
            price=118910.0,
            volume=15,
        ),
        PricePoint(
            ticker="BTC-USD",
            timestamp=datetime(2026, 7, 12, 10, 30, tzinfo=timezone.utc),
            price=118420.0,
            volume=9,
        ),
        PricePoint(
            ticker="BTC-USD",
            timestamp=datetime(2026, 7, 12, 11, 0, tzinfo=timezone.utc),
            price=119300.0,
            volume=18,
        ),
        PricePoint(
            ticker="BTC-USD",
            timestamp=datetime(2026, 7, 12, 11, 30, tzinfo=timezone.utc),
            price=119850.0,
            volume=16,
        ),
    ],
}
