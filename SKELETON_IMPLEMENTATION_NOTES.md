# Skeleton Implementation Notes

## Goal

Create a simple first version of the real-time market data pipeline that is easy to run, test, and extend later.

The first version intentionally avoids Kafka, PostgreSQL, and Redis so the API contract and metric logic can be built before adding infrastructure complexity.

## What Was Implemented

The initial skeleton includes:

- A FastAPI application.
- In-memory market data for a few sample tickers.
- REST endpoints for latest prices, historical prices, metrics, and market summary data.
- A small service layer for market data lookup and metric calculations.
- Pydantic models for API responses.
- Basic pytest coverage.
- Docker and Docker Compose scaffolding.
- A README with local setup and run commands.

## Project Structure

```text
real-time_market/
├── market_pipeline/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── sample_data.py
│   └── services.py
├── tests/
│   └── test_api.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── PROJECT_DESCRIPTION.md
```

## Design Approach

The skeleton was split into a few small pieces:

- `main.py` owns the FastAPI routes.
- `models.py` defines the API response shapes.
- `sample_data.py` provides temporary in-memory market data.
- `services.py` contains the business logic for price lookup and metric calculations.
- `tests/test_api.py` verifies the API behavior.

This keeps the app simple now, while leaving a clear path to replace the in-memory data with PostgreSQL, Redis, and Kafka-backed services later.

## API Endpoints Added

```text
GET /health
GET /prices/latest/{ticker}
GET /prices/history/{ticker}
GET /metrics/{ticker}
GET /market/summary
```

## Metrics Implemented

The first version calculates:

- 3-point moving average
- 5-point moving average
- latest return percentage
- volatility percentage
- VWAP
- price change percentage

These calculations currently use simple Python logic over in-memory data. Pandas can be introduced later when the data volume or processing complexity justifies it.

## Problems Encountered And Fixes

### 1. `python` Was Not Available

The environment did not have `python` on the path.

Fix:

```bash
python3
```

was used instead.

### 2. `pytest` Was Not Installed

The initial test run failed because the environment did not have pytest installed.

Fix:

- Created a local virtual environment.
- Installed the project with development dependencies.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

### 3. Dependency Installation Needed Network Access

The first dependency install failed because the sandbox could not reach the Python package index.

Fix:

The install was rerun with network approval, then dependencies installed successfully.

### 4. FastAPI Test Client Hung

The first tests used FastAPI's synchronous `TestClient`, but requests hung during execution.

The stack trace showed that FastAPI was trying to run synchronous endpoint functions through AnyIO's threadpool, where the request stalled in this environment.

Fixes:

- Converted route handlers in `main.py` from regular `def` functions to `async def`.
- Switched tests to use `httpx.AsyncClient` with `ASGITransport`.

This made the tests run directly against the ASGI app without depending on the synchronous test-client wrapper.

### 5. Newer Dependency Versions Caused Test-Client Churn

An early install pulled very new FastAPI/Starlette versions and produced a deprecation warning around the test client stack.

Fix:

The dependency ranges in `pyproject.toml` were pinned conservatively:

```toml
fastapi>=0.115.0,<0.116.0
uvicorn[standard]>=0.30.0,<0.31.0
httpx>=0.27.0,<0.28.0
pytest>=8.2.0,<9.0.0
ruff>=0.5.0,<0.6.0
```

This gives the project a more predictable starter environment.

### 6. Editable Install Generated Metadata

Installing the project locally created `real_time_market.egg-info/`.

Fix:

Added this pattern to `.gitignore`:

```text
*.egg-info/
```

## Verification

The final skeleton was verified with:

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check .
timeout 5 .venv/bin/uvicorn market_pipeline.main:app --host 127.0.0.1 --port 8000
```

Results:

- 6 tests passed.
- Ruff linting passed.
- Uvicorn started the app successfully.

## Why This Skeleton Is Useful

This version gives the project a working baseline:

- API routes already exist.
- Response models are defined.
- Metric behavior has tests.
- Docker setup is ready.
- The service layer can be replaced with real infrastructure later.

The next implementation step should be adding a repository layer and PostgreSQL schema, while keeping the current in-memory data source useful for local tests.
