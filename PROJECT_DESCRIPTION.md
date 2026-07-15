# Real-Time Market Data Pipeline

## Overview

Build a real-time market data platform that ingests stock, ETF, or crypto price events, streams them through Kafka, processes financial metrics, stores historical data, and exposes analytics through REST APIs.

## Recommended CV Title

**Real-Time Market Data Pipeline**

## Technology Stack

- Python
- FastAPI
- Kafka
- PostgreSQL
- Redis
- Docker
- Kubernetes
- Pandas
- GitLab CI/CD

## Core Features

- Ingest simulated or real market price data for stocks, ETFs, or crypto assets.
- Publish market events to Kafka topics for asynchronous processing.
- Build Python consumers to calculate financial metrics:
  - Moving averages
  - Daily returns
  - Volatility
  - VWAP
  - Price change percentages
- Store raw and processed market data in PostgreSQL.
- Use Redis to cache latest prices and frequently requested metrics.
- Expose REST APIs with FastAPI for market data and analytics.
- Containerize services with Docker.
- Deploy locally with Docker Compose.
- Optionally deploy to Kubernetes.
- Add a CI/CD pipeline for testing, Docker image builds, and deployment.

## Example API Endpoints

```text
GET /prices/latest/{ticker}
GET /prices/history/{ticker}
GET /metrics/{ticker}
GET /market/summary
```

## High-Level Architecture

```text
Market Data Source
        |
        v
Producer Service
        |
        v
Kafka Topics
        |
        v
Consumer / Metrics Processor
        |
        +--> PostgreSQL: raw events and historical metrics
        |
        +--> Redis: latest prices and frequently requested metrics
        |
        v
FastAPI Service
        |
        v
REST API Clients
```

## Resume Bullet Version

- Built a real-time market data pipeline using Python, Kafka, FastAPI, PostgreSQL, Redis, Docker, and Kubernetes to ingest, process, and expose financial market analytics.
- Implemented event-driven consumers to calculate moving averages, volatility, VWAP, returns, and price change metrics from streamed market data.
- Designed REST APIs for querying latest prices, historical data, and processed analytics, with Redis caching for low-latency responses.

## Potential Implementation Milestones

1. Create the FastAPI service skeleton and health check endpoint.
2. Add PostgreSQL schema for raw prices and processed metrics.
3. Add Redis integration for latest price caching.
4. Build a market data producer for simulated price events.
5. Configure Kafka topics and consumer workers.
6. Implement metric calculations with Python and Pandas.
7. Expose REST endpoints for prices, metrics, and market summary data.
8. Add Docker Compose for local development.
9. Add tests for API behavior and metric calculations.
10. Add GitLab CI/CD for testing, image builds, and deployment steps.
