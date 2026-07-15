from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    UniqueConstraint,
    desc,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class ORMBase(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


class Instrument(ORMBase):
    __tablename__ = "instruments"
    __table_args__ = (
        CheckConstraint("length(trim(ticker)) > 0", name="instruments_ticker_not_empty"),
        CheckConstraint("length(trim(currency)) > 0", name="instruments_currency_not_empty"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    asset_type: Mapped[str] = mapped_column(Text, nullable=False, server_default="unknown")
    name: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(Text, nullable=False, server_default="USD")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    price_events: Mapped[list[PriceEvent]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    market_metrics: Mapped[list[MarketMetric]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    latest_market_price: Mapped[LatestMarketPrice | None] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PriceEvent(ORMBase):
    __tablename__ = "price_events"
    __table_args__ = (
        CheckConstraint("price > 0", name="price_events_price_positive"),
        CheckConstraint("volume >= 0", name="price_events_volume_non_negative"),
        CheckConstraint("length(trim(source)) > 0", name="price_events_source_not_empty"),
        UniqueConstraint(
            "instrument_id",
            "event_time",
            "source",
            name="price_events_instrument_time_source_unique",
        ),
        Index("price_events_instrument_time_idx", "instrument_id", desc("event_time")),
        Index("price_events_time_idx", desc("event_time")),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(Text, nullable=False, server_default="unknown")
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    instrument: Mapped[Instrument] = relationship(back_populates="price_events")
    latest_market_price: Mapped[LatestMarketPrice | None] = relationship(
        back_populates="last_price_event"
    )


class MarketMetric(ORMBase):
    __tablename__ = "market_metrics"
    __table_args__ = (
        CheckConstraint("window_start <= window_end", name="market_metrics_window_valid"),
        CheckConstraint("latest_price > 0", name="market_metrics_latest_price_positive"),
        CheckConstraint("moving_average_3 > 0", name="market_metrics_moving_average_3_positive"),
        CheckConstraint("moving_average_5 > 0", name="market_metrics_moving_average_5_positive"),
        CheckConstraint("vwap >= 0", name="market_metrics_vwap_non_negative"),
        UniqueConstraint(
            "instrument_id",
            "window_end",
            name="market_metrics_instrument_window_unique",
        ),
        Index("market_metrics_instrument_window_idx", "instrument_id", desc("window_end")),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
    )
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latest_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    moving_average_3: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    moving_average_5: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    latest_return_percent: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    volatility_percent: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    vwap: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    price_change_percent: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    instrument: Mapped[Instrument] = relationship(back_populates="market_metrics")


class LatestMarketPrice(ORMBase):
    __tablename__ = "latest_market_prices"
    __table_args__ = (
        CheckConstraint("price > 0", name="latest_market_prices_price_positive"),
        CheckConstraint("volume >= 0", name="latest_market_prices_volume_non_negative"),
    )

    instrument_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_price_event_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("price_events.id", ondelete="SET NULL"),
    )
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    instrument: Mapped[Instrument] = relationship(back_populates="latest_market_price")
    last_price_event: Mapped[PriceEvent | None] = relationship(
        back_populates="latest_market_price"
    )


class PricePoint(PydanticBaseModel):
    ticker: str = Field(..., examples=["AAPL"])
    timestamp: datetime
    price: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)


class LatestPrice(PydanticBaseModel):
    ticker: str
    timestamp: datetime
    price: float
    volume: int


class Metrics(PydanticBaseModel):
    ticker: str
    latest_price: float
    moving_average_3: float
    moving_average_5: float
    latest_return_percent: float
    volatility_percent: float
    vwap: float
    price_change_percent: float


class MarketSummaryItem(PydanticBaseModel):
    ticker: str
    latest_price: float
    price_change_percent: float
    volume: int


class MarketSummary(PydanticBaseModel):
    tickers: int
    total_volume: int
    items: list[MarketSummaryItem]
