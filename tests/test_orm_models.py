from sqlalchemy.orm import configure_mappers

from market_pipeline.models import ORMBase


def test_sqlalchemy_models_map_market_tables() -> None:
    configure_mappers()

    assert set(ORMBase.metadata.tables) == {
        "instruments",
        "latest_market_prices",
        "market_metrics",
        "price_events",
    }


def test_price_events_indexes_match_schema() -> None:
    price_events = ORMBase.metadata.tables["price_events"]
    index_names = {index.name for index in price_events.indexes}

    assert index_names == {
        "price_events_instrument_time_idx",
        "price_events_time_idx",
    }
