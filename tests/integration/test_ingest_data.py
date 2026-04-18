import pytest
from datetime import datetime
from typing import Any

from clearmetrics.application.ingest_data import IngestDataUseCase
from clearmetrics.domain.services.etl_service import ETLService
from clearmetrics.domain.models.transaction import Transaction
from clearmetrics.domain.exceptions import DomainException
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


@pytest.fixture
def use_case() -> IngestDataUseCase:
    etl = ETLService(
        source=FakeTransactionSource([RAW]),
        storage=FakeTransactionStorage(),
    )
    return IngestDataUseCase(etl_service=etl)


class TestIngestDataUseCase:
    def test_admin_can_ingest(self, use_case: IngestDataUseCase) -> None:
        result = use_case.execute(filters={}, user_role="admin")
        assert len(result) == 1
        assert isinstance(result[0], Transaction)

    def test_analyst_can_ingest(self, use_case: IngestDataUseCase) -> None:
        result = use_case.execute(filters={}, user_role="analyst")
        assert len(result) == 1

    def test_viewer_cannot_ingest(self, use_case: IngestDataUseCase) -> None:
        with pytest.raises(PermissionError):
            use_case.execute(filters={}, user_role="viewer")

    def test_unknown_role_cannot_ingest(self, use_case: IngestDataUseCase) -> None:
        with pytest.raises(PermissionError):
            use_case.execute(filters={}, user_role="unknown")

    def test_execute_passes_filters_to_etl(self) -> None:
        received: list[dict[str, Any]] = []

        class CapturingSource(ITransactionSourcePort):
            def fetch_transactions(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
                received.append(filters)
                return []

        etl = ETLService(source=CapturingSource(), storage=FakeTransactionStorage())
        use_case = IngestDataUseCase(etl_service=etl)
        use_case.execute(filters={"account_id": "acc-001"}, user_role="admin")
        assert received[0] == {"account_id": "acc-001"}

    def test_execute_returns_empty_on_no_records(self) -> None:
        etl = ETLService(
            source=FakeTransactionSource([]),
            storage=FakeTransactionStorage(),
        )
        use_case = IngestDataUseCase(etl_service=etl)
        result = use_case.execute(filters={}, user_role="admin")
        assert result == []
