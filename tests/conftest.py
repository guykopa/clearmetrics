import os
import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_MINUTES", "60")
os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost:5432/clearmetrics_test")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture
def raw_transaction_data() -> dict:
    return {
        "id": "txn-001",
        "amount": 150.75,
        "currency": "EUR",
        "account_id": "acc-001",
        "timestamp": "2024-01-15T10:30:00",
        "source": "postgresql",
    }


@pytest.fixture
def raw_metric_data() -> dict:
    return {
        "name": "revenue",
        "value": 10000.0,
        "unit": "EUR",
        "timestamp": "2024-01-15T10:30:00",
        "dimensions": {"region": "EU", "product": "A"},
    }


@pytest.fixture
def raw_user_data() -> dict:
    return {
        "id": "usr-001",
        "email": "analyst@clearmetrics.io",
        "role": "analyst",
        "hashed_password": "hashed_secret",
    }
