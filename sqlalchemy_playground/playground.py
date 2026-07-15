from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


DATABASE_PATH = Path(__file__).with_name("playground.db")


class Base(DeclarativeBase):
    pass


class Instrument(Base):
    __tablename__ = "instruments"
    __table_args__ = (
        CheckConstraint("length(trim(ticker)) > 0", name="ticker_not_empty"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    asset_type: Mapped[str] = mapped_column(String, nullable=False, default="unknown")
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    name: Mapped[str | None] = mapped_column(String)

    price_events: Mapped[list[PriceEvent]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Instrument(id={self.id!r}, ticker={self.ticker!r})"


class PriceEvent(Base):
    __tablename__ = "price_events"
    __table_args__ = (
        CheckConstraint("price > 0", name="price_positive"),
        CheckConstraint("volume >= 0", name="volume_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)

    instrument: Mapped[Instrument] = relationship(back_populates="price_events")

    def __repr__(self) -> str:
        return (
            "PriceEvent("
            f"id={self.id!r}, ticker={self.instrument.ticker!r}, "
            f"price={self.price!r}, volume={self.volume!r})"
        )


def reset_database() -> None:
    engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def get_session() -> Session:
    engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
    return Session(engine)


def seed_data(session: Session) -> None:
    apple = Instrument(ticker="AAPL", asset_type="stock", currency="USD")
    bitcoin = Instrument(ticker="BTC-USD", asset_type="crypto", currency="USD")
    nvidia = Instrument(ticker="NVDA", asset_type="stock", currency="USD")

    apple.price_events = [
        PriceEvent(
            event_time=datetime(2026, 7, 12, 9, 30, tzinfo=timezone.utc),
            price=Decimal("195.12"),
            volume=Decimal("1250"),
        ),
        PriceEvent(
            event_time=datetime(2026, 7, 12, 10, 0, tzinfo=timezone.utc),
            price=Decimal("196.03"),
            volume=Decimal("2100"),
        ),
        PriceEvent(
            event_time=datetime(2026, 7, 12, 10, 30, tzinfo=timezone.utc),
            price=Decimal("195.64"),
            volume=Decimal("1840"),
        ),
    ]

    bitcoin.price_events = [
        PriceEvent(
            event_time=datetime(2026, 7, 12, 9, 30, tzinfo=timezone.utc),
            price=Decimal("118250.00"),
            volume=Decimal("12"),
        ),
        PriceEvent(
            event_time=datetime(2026, 7, 12, 10, 0, tzinfo=timezone.utc),
            price=Decimal("118910.00"),
            volume=Decimal("15"),
        ),
    ]

    nvidia.price_events = [
        PriceEvent(
            event_time=datetime(2026, 7, 12, 9, 30, tzinfo=timezone.utc),
            price=Decimal("118250.00"),
            volume=Decimal("12"),
        ),
        PriceEvent(
            event_time=datetime(2026, 7, 12, 10, 30, tzinfo=timezone.utc),
            price=Decimal("118670.00"),
            volume=Decimal("30"),
        ),
    ]

    session.add_all([apple, bitcoin, nvidia])
    session.commit()


def print_instruments(session: Session) -> None:
    statement = select(Instrument).order_by(Instrument.ticker)
    instruments = session.scalars(statement).all()

    print("Instruments:")
    for instrument in instruments:
        print(f"- {instrument.ticker} ({instrument.asset_type})")


def print_price_events(session: Session) -> None:
    statement = (
        select(PriceEvent)
        .join(PriceEvent.instrument)
        .order_by(Instrument.ticker, PriceEvent.event_time)
    )
    price_events = session.scalars(statement).all()

    print("\nPrice events:")
    for event in price_events:
        print(f"- {event.instrument.ticker}: {event.price} volume={event.volume}")


def print_history_for_ticker(session: Session, ticker: str) -> None:
    instrument_statement = select(Instrument).where(Instrument.ticker == ticker)
    instrument = session.scalars(instrument_statement).one_or_none()

    if instrument is None:
        print(f"\nNo instrument found for ticker: {ticker}")
        return

    price_event_statement = (
        select(PriceEvent)
        .where(PriceEvent.instrument_id == instrument.id)
        .order_by(PriceEvent.event_time)
    )
    price_events = session.scalars(price_event_statement).all()

    print(f"\nPrice history for {ticker}:")
    for event in price_events:
        print(f"- {event.event_time}: {event.price} volume={event.volume}")

def latest_price(session: Session, ticker: str) -> PriceEvent | None:
    instrument_statement = select(Instrument).where(Instrument.ticker == ticker)
    instrument = session.scalars(instrument_statement).one_or_none()

    if instrument is None:
        return None
    
    price_event_statement = (
        select(PriceEvent)
        .where(PriceEvent.instrument_id == instrument.id)
        .order_by(PriceEvent.event_time.desc())
    )

    return session.scalars(price_event_statement).first()

def print_total_volume_by_ticker(session: Session) -> None:
    statement = (
        select(
            Instrument.ticker,
            func.sum(PriceEvent.volume),
        )
        .join(PriceEvent.instrument)
        .group_by(Instrument.ticker)
        .order_by(Instrument.ticker)
    )

    results = session.execute(statement).all()

    print("\nTotal_volume by ticker:")
    for ticker, total_volume in results:
        print(f"- {ticker}: {total_volume}")

def rename_instrument(session: Session, ticker: str, name: str) -> None:
    statement = select(Instrument).where(Instrument.ticker == ticker)
    instrument = session.scalars(statement).one_or_none()

    if instrument is None:
        print(f"\nNo instrument found for ticker: {ticker}")
        return

    instrument.name = name
    session.commit()

    refreshed_statement = select(Instrument).where(Instrument.ticker == ticker)
    refreshed_instrument = session.scalars(refreshed_statement).one()

    print(f"\nUpdated instrument:")
    print(f"- {refreshed_instrument.ticker}: {refreshed_instrument.name}")


def delete_instrument_and_check_events(session: Session, ticker: str) -> None:
    instrument = session.scalars(
        select(Instrument).where(Instrument.ticker == ticker)
    ).one_or_none()

    if instrument is None:
        print(f"\nNo instrument found for ticker: {ticker}")
        return
    
    before_count = session.scalars(
        select(PriceEvent).where(PriceEvent.instrument_id == instrument.id)
    ).all()
    
    print(f"\nBefore delete, {ticker} has {len(before_count)} price events")

    session.delete(instrument)
    session.commit()

    after_count = session.scalars(
        select(PriceEvent).where(PriceEvent.instrument_id == instrument.id)
    )
    print(f"After delete, {ticker} has {len(after_count)} price events")

def main() -> None:
    reset_database()

    with get_session() as session:
        seed_data(session)
        print_instruments(session)
        print_price_events(session)
        print_history_for_ticker(session, "AAPL")
        print_history_for_ticker(session, "UNKNOWN")

        event = latest_price(session, "AAPL")

        if event is None:
            print("No latest price found")
        else:
            print(f"{event.instrument.ticker}: {event.price} at {event.event_time}")
        
        print_total_volume_by_ticker(session)

        rename_instrument(session, "AAPL", "Apple Inc.")


    print(f"\nDatabase created at: {DATABASE_PATH}")



if __name__ == "__main__":
    main()
