CREATE TABLE instruments (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    asset_type TEXT NOT NULL DEFAULT 'unknown',
    name TEXT,
    currency TEXT NOT NULL DEFAULT 'USD',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT instruments_ticker_not_empty CHECK (length(trim(ticker)) > 0),
    CONSTRAINT instruments_currency_not_empty CHECK (length(trim(currency)) > 0)
);

CREATE TABLE price_events (
    id BIGSERIAL PRIMARY KEY,
    instrument_id BIGINT NOT NULL REFERENCES instruments (id) ON DELETE CASCADE,
    source TEXT NOT NULL DEFAULT 'unknown',
    event_time TIMESTAMPTZ NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    volume NUMERIC(20, 8) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT price_events_price_positive CHECK (price > 0),
    CONSTRAINT price_events_volume_non_negative CHECK (volume >= 0),
    CONSTRAINT price_events_source_not_empty CHECK (length(trim(source)) > 0),
    CONSTRAINT price_events_instrument_time_source_unique UNIQUE (
        instrument_id,
        event_time,
        source
    )
);

CREATE INDEX price_events_instrument_time_idx
    ON price_events (instrument_id, event_time DESC);

CREATE INDEX price_events_time_idx
    ON price_events (event_time DESC);

CREATE TABLE market_metrics (
    id BIGSERIAL PRIMARY KEY,
    instrument_id BIGINT NOT NULL REFERENCES instruments (id) ON DELETE CASCADE,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    latest_price NUMERIC(20, 8) NOT NULL,
    moving_average_3 NUMERIC(20, 8) NOT NULL,
    moving_average_5 NUMERIC(20, 8) NOT NULL,
    latest_return_percent NUMERIC(12, 6) NOT NULL,
    volatility_percent NUMERIC(12, 6) NOT NULL,
    vwap NUMERIC(20, 8) NOT NULL,
    price_change_percent NUMERIC(12, 6) NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT market_metrics_window_valid CHECK (window_start <= window_end),
    CONSTRAINT market_metrics_latest_price_positive CHECK (latest_price > 0),
    CONSTRAINT market_metrics_moving_average_3_positive CHECK (moving_average_3 > 0),
    CONSTRAINT market_metrics_moving_average_5_positive CHECK (moving_average_5 > 0),
    CONSTRAINT market_metrics_vwap_non_negative CHECK (vwap >= 0),
    CONSTRAINT market_metrics_instrument_window_unique UNIQUE (instrument_id, window_end)
);

CREATE INDEX market_metrics_instrument_window_idx
    ON market_metrics (instrument_id, window_end DESC);

CREATE TABLE latest_market_prices (
    instrument_id BIGINT PRIMARY KEY REFERENCES instruments (id) ON DELETE CASCADE,
    last_price_event_id BIGINT REFERENCES price_events (id) ON DELETE SET NULL,
    event_time TIMESTAMPTZ NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    volume NUMERIC(20, 8) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT latest_market_prices_price_positive CHECK (price > 0),
    CONSTRAINT latest_market_prices_volume_non_negative CHECK (volume >= 0)
);

CREATE OR REPLACE FUNCTION refresh_latest_market_prices()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO latest_market_prices (
        instrument_id,
        last_price_event_id,
        event_time,
        price,
        volume,
        updated_at
    )
    VALUES (
        NEW.instrument_id,
        NEW.id,
        NEW.event_time,
        NEW.price,
        NEW.volume,
        now()
    )
    ON CONFLICT (instrument_id) DO UPDATE
    SET
        last_price_event_id = EXCLUDED.last_price_event_id,
        event_time = EXCLUDED.event_time,
        price = EXCLUDED.price,
        volume = EXCLUDED.volume,
        updated_at = now()
    WHERE latest_market_prices.event_time <= EXCLUDED.event_time;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER refresh_latest_market_prices_after_insert
AFTER INSERT ON price_events
FOR EACH ROW
EXECUTE FUNCTION refresh_latest_market_prices();
