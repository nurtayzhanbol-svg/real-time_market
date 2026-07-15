# Real-Time Market Data Pipeline

Simple first version of a real-time market data pipeline. This skeleton exposes FastAPI endpoints backed by in-memory seed data so the API contract and metric calculations can be developed before adding Kafka, PostgreSQL, and Redis.

## Current Features

- FastAPI application with health, price, metrics, and market summary endpoints.
- In-memory seed market data for stocks and crypto.
- Repository layer for market data access.
- Basic calculations for moving averages, returns, volatility, VWAP, and price change percentage.
- Docker and Docker Compose scaffolding.
- PostgreSQL schema for instruments, raw price events, latest prices, and calculated metrics.
- Pytest coverage for the initial API behavior.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn market_pipeline.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Run With Docker

```bash
docker compose up --build
```

PostgreSQL initializes the market tables from `database/schema.sql` the first time
the `postgres_data` volume is created. To rerun the init script from scratch,
remove the volume with:

```bash
docker compose down -v
```

## Run Tests

```bash
pytest
```

## API Endpoints

```text
GET /health
GET /prices/latest/{ticker}
GET /prices/history/{ticker}
GET /metrics/{ticker}
GET /market/summary
```

## Next Milestones

1. Add Redis for latest price and metrics caching.
2. Add a Kafka producer for simulated market events.
3. Add Kafka consumers for metric processing.
4. Replace in-memory data with repository interfaces backed by PostgreSQL and Redis.
5. Add GitLab CI/CD for tests and Docker image builds.
