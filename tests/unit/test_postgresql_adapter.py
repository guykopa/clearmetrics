import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clearmetrics.adapters.outbound.postgresql_models import Base
from clearmetrics.adapters.outbound.postgresql_transaction_source_adapter import PostgreSQLTransactionSourceAdapter
from clearmetrics.adapters.outbound.postgresql_transaction_storage_adapter import PostgreSQLTransactionStorageAdapter
from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort
from clearmetrics.ports.outbound.i_transaction_storage_port import ITransactionStoragePort

RAW = {
    "id": "txn-001",
    "amount": 150.75,
    "currency": "EUR",
    "account_id": "acc-001",
    "timestamp": datetime(2024, 1, 15, 10, 30),
    "source": "postgresql",
}


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


class TestPostgreSQLTransactionSourceAdapter:
    def test_implements_port(self, session: Session) -> None:
        adapter = PostgreSQLTransactionSourceAdapter(session=session)
        assert isinstance(adapter, ITransactionSourcePort)

    def test_fetch_returns_empty_when_no_records(self, session: Session) -> None:
        adapter = PostgreSQLTransactionSourceAdapter(session=session)
        result = adapter.fetch_transactions(filters={})
        assert result == []

    def test_fetch_returns_saved_transaction(self, session: Session) -> None:
        storage = PostgreSQLTransactionStorageAdapter(session=session)
        storage.save_transaction(RAW)
        session.commit()

        source = PostgreSQLTransactionSourceAdapter(session=session)
        result = source.fetch_transactions(filters={})
        assert len(result) == 1
        assert result[0]["id"] == "txn-001"

    def test_fetch_filters_by_account_id(self, session: Session) -> None:
        storage = PostgreSQLTransactionStorageAdapter(session=session)
        storage.save_transaction(RAW)
        storage.save_transaction({**RAW, "id": "txn-002", "account_id": "acc-999"})
        session.commit()

        source = PostgreSQLTransactionSourceAdapter(session=session)
        result = source.fetch_transactions(filters={"account_id": "acc-001"})
        assert len(result) == 1
        assert result[0]["account_id"] == "acc-001"

    def test_fetch_returns_all_when_no_filters(self, session: Session) -> None:
        storage = PostgreSQLTransactionStorageAdapter(session=session)
        storage.save_transaction(RAW)
        storage.save_transaction({**RAW, "id": "txn-002"})
        session.commit()

        source = PostgreSQLTransactionSourceAdapter(session=session)
        result = source.fetch_transactions(filters={})
        assert len(result) == 2


class TestPostgreSQLTransactionStorageAdapter:
    def test_implements_port(self, session: Session) -> None:
        adapter = PostgreSQLTransactionStorageAdapter(session=session)
        assert isinstance(adapter, ITransactionStoragePort)

    def test_save_persists_transaction(self, session: Session) -> None:
        adapter = PostgreSQLTransactionStorageAdapter(session=session)
        adapter.save_transaction(RAW)
        session.commit()

        source = PostgreSQLTransactionSourceAdapter(session=session)
        result = source.fetch_transactions(filters={})
        assert len(result) == 1

    def test_save_stores_all_fields(self, session: Session) -> None:
        adapter = PostgreSQLTransactionStorageAdapter(session=session)
        adapter.save_transaction(RAW)
        session.commit()

        source = PostgreSQLTransactionSourceAdapter(session=session)
        record = source.fetch_transactions(filters={})[0]
        assert record["id"] == RAW["id"]
        assert record["amount"] == RAW["amount"]
        assert record["currency"] == RAW["currency"]
        assert record["account_id"] == RAW["account_id"]
        assert record["source"] == RAW["source"]
