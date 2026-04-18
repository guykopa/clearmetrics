from datetime import datetime
from typing import Any

from clearmetrics.domain.services.etl_service import ETLService
from clearmetrics.domain.models.transaction import Transaction
from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort
from clearmetrics.ports.outbound.i_transaction_storage_port import ITransactionStoragePort


class FakeTransactionSource(ITransactionSourcePort):
    def __init__(self, records: list[dict[str, Any]]) -> None:
        self._records = records

    def fetch_transactions(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        return self._records


class FakeTransactionStorage(ITransactionStoragePort):
    def __init__(self) -> None:
        self.saved: list[dict[str, Any]] = []

    def save_transaction(self, transaction: dict[str, Any]) -> None:
        self.saved.append(transaction)


RAW = {
    "id": "txn-001",
    "amount": 150.75,
    "currency": "EUR",
    "account_id": "acc-001",
    "timestamp": datetime(2024, 1, 15, 10, 30),
    "source": "postgresql",
}


class TestETLService:
    def test_run_returns_transaction_objects(self) -> None:
        service = ETLService(
            source=FakeTransactionSource([RAW]),
            storage=FakeTransactionStorage(),
        )
        result = service.run(filters={})
        assert len(result) == 1
        assert isinstance(result[0], Transaction)

    def test_run_saves_each_transaction(self) -> None:
        storage = FakeTransactionStorage()
        service = ETLService(source=FakeTransactionSource([RAW]), storage=storage)
        service.run(filters={})
        assert len(storage.saved) == 1

    def test_run_returns_empty_on_no_records(self) -> None:
        service = ETLService(
            source=FakeTransactionSource([]),
            storage=FakeTransactionStorage(),
        )
        assert service.run(filters={}) == []

    def test_run_transforms_multiple_records(self) -> None:
        records = [{**RAW, "id": f"txn-{i:03d}"} for i in range(5)]
        storage = FakeTransactionStorage()
        service = ETLService(source=FakeTransactionSource(records), storage=storage)
        result = service.run(filters={})
        assert len(result) == 5
        assert len(storage.saved) == 5

    def test_run_skips_invalid_records(self) -> None:
        invalid = {**RAW, "amount": -100.0}
        storage = FakeTransactionStorage()
        service = ETLService(
            source=FakeTransactionSource([RAW, invalid]),
            storage=storage,
        )
        result = service.run(filters={})
        assert len(result) == 1
        assert len(storage.saved) == 1

    def test_run_passes_filters_to_source(self) -> None:
        received: list[dict[str, Any]] = []

        class CapturingSource(ITransactionSourcePort):
            def fetch_transactions(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
                received.append(filters)
                return []

        service = ETLService(source=CapturingSource(), storage=FakeTransactionStorage())
        service.run(filters={"account_id": "acc-001"})
        assert received[0] == {"account_id": "acc-001"}

    def test_service_depends_on_ports_not_adapters(self) -> None:
        source = FakeTransactionSource([])
        storage = FakeTransactionStorage()
        service = ETLService(source=source, storage=storage)
        assert isinstance(service._source, ITransactionSourcePort)
        assert isinstance(service._storage, ITransactionStoragePort)
