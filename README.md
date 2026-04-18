# clearmetrics

Python BI platform for ingesting, transforming, validating, and visualizing financial data from multiple sources.

**Documentation:** [https://guykopa.github.io/clearmetrics/](https://guykopa.github.io/clearmetrics/)

## Features

- Ingest data from PostgreSQL, CSV files, and external REST APIs
- Transform and aggregate data via an ETL pipeline (pandas)
- Validate data quality with automated rules (NotNull, PositiveAmount, ValidCurrency, NoDuplicate, DateRange)
- Expose metrics via a secured REST API (FastAPI + JWT)
- Display an interactive dashboard (Chart.js, filters, CSV export)
- Role-based access control (admin / analyst / viewer)
- Real-time monitoring (Prometheus + Grafana)
- Deploy via Docker and GitHub Actions CI/CD

## Architecture

Hexagonal Architecture (Ports & Adapters). The domain layer never imports from adapters, infrastructure, or the application layer. See [ARCHITECTURE.md](ARCHITECTURE.md) for full details.

```
HTTP Request → FastAPI (inbound adapter)
                 → Use Case (application)
                   → Domain Service
                     → Port (interface)
                       → Adapter (PostgreSQL / CSV / API / JWT)
```

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Pydantic, uvicorn |
| ORM | SQLAlchemy |
| Auth | PyJWT |
| ETL | pandas |
| Monitoring | structlog, Prometheus, Grafana |
| Testing | pytest, pytest-cov |
| Linting | flake8, mypy |
| Docs | Sphinx, sphinx-autodoc-typehints |
| Deploy | Docker, docker-compose, GitHub Actions |

## Quick start

```bash
# 1. Clone and set up environment
git clone https://github.com/your-org/clearmetrics.git
cd clearmetrics
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Edit .env with your values

# 3. Start all services
docker-compose -f docker/docker-compose.yml up -d

# 4. Initialize the database
DATABASE_URL=... bash scripts/init_db.sh

# 5. Check health
bash scripts/health_check.sh
```

## Services

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Dashboard | http://localhost:8080 |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| Documentation | https://guykopa.github.io/clearmetrics/ |

## API endpoints

| Method | Endpoint | Role |
|---|---|---|
| GET | `/health` | public |
| POST | `/auth/token` | public |
| POST | `/api/transactions/ingest` | admin, analyst |
| GET | `/api/metrics` | admin, analyst, viewer |
| GET | `/metrics` | Prometheus scrape |

## Running tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/ tests/non_regression/

# With coverage
pytest --cov=clearmetrics --cov-report=html
```

## Development

```bash
# Lint
flake8 clearmetrics/

# Type check
mypy clearmetrics/

# Build docs
sphinx-build -b html docs/ docs/_build/
```

## Role permissions

| Action | admin | analyst | viewer |
|---|---|---|---|
| Ingest data | ✓ | ✓ | |
| Validate data | ✓ | ✓ | |
| Export metrics | ✓ | ✓ | ✓ |
| Manage users | ✓ | | |

## Adding a new quality rule

1. Create `tests/unit/test_my_rule.py` (RED)
2. Create `clearmetrics/domain/rules/my_rule.py` implementing `IQualityRulePort` (GREEN)
3. Register the rule in `clearmetrics/cli/main.py`

Never modify existing rules — add new files only (Open/Closed principle).
