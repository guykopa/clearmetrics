"""
Non-regression tests for the ETL pipeline.
These tests lock the behaviour of the full ETL + quality pipeline
on known datasets. If any test breaks here, a regression was introduced.
"""
from datetime import datetime
from typing import Any

from clearmetrics.domain.services.etl_service import ETLService
from clearmetrics.domain.services.quality_service import QualityService
from clearmetrics.domain.rules.not_null_rule import NotNullRule
from clearmetrics.domain.rules.positive_amount_rule import PositiveAmountRule
from clearmetrics.domain.rules.valid_currency_rule import ValidCurrencyRule
from clearmetrics.domain.rules.no_duplicate_rule import NoDuplicateRule
from clearmetrics.domain.rules.date_range_rule import DateRangeRule
from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort
from clearmetrics.ports.outbound.i_transaction_storage_port import ITransactionStoragePort


class FakeSource(ITransactionSourcePort):
    def __init__(self, records: list[dict[str, Any]]) -> None:
        self._records = records

    def fetch_transactions(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        return self._records


class FakeStorage(ITransactionStoragePort):
    def __init__(self) -> None:
        self.saved: list[dict[str, Any]] = []

    def save_transaction(self, transaction: dict[str, Any]) -> None:
        self.saved.append(transaction)


VALID_RECORDS = [
    {"id": "txn-001", "amount": 100.0, "currency": "EUR", "account_id": "acc-001",
     "timestamp": datetime(2024, 6, 1), "source": "postgresql"},
    {"id": "txn-002", "amount": 250.0, "currency": "USD", "account_id": "acc-002",
     "timestamp": datetime(2024, 6, 2), "source": "csv"},
    {"id": "txn-003", "amount": 75.5, "currency": "GBP", "account_id": "acc-001",
     "timestamp": datetime(2024, 6, 3), "source": "external_api"},
]

MIXED_RECORDS = [
    *VALID_RECORDS,
    {"id": "txn-004", "amount": -50.0, "currency": "EUR", "account_id": "acc-001",
     "timestamp": datetime(2024, 6, 4), "source": "postgresql"},
    {"id": "txn-005", "amount": 200.0, "currency": "INVALID", "account_id": "acc-002",
     "timestamp": datetime(2024, 6, 5), "source": "csv"},
]


class TestETLStability:
    def test_valid_dataset_produces_correct_transaction_count(self) -> None:
        storage = FakeStorage()
        etl = ETLService(source=FakeSource(VALID_RECORDS), storage=storage)
        result = etl.run(filters={})
        assert len(result) == 3

    def test_etl_saves_exactly_as_many_as_it_returns(self) -> None:
        storage = FakeStorage()
        etl = ETLService(source=FakeSource(VALID_RECORDS), storage=storage)
        result = etl.run(filters={})
        assert len(storage.saved) == len(result)

    def test_invalid_records_are_filtered_out(self) -> None:
        storage = FakeStorage()
        etl = ETLService(source=FakeSource(MIXED_RECORDS), storage=storage)
        result = etl.run(filters={})
        assert len(result) == 3

    def test_transaction_ids_are_preserved(self) -> None:
        storage = FakeStorage()
        etl = ETLService(source=FakeSource(VALID_RECORDS), storage=storage)
        result = etl.run(filters={})
        ids = {t.id for t in result}
        assert ids == {"txn-001", "txn-002", "txn-003"}

    def test_amounts_are_preserved(self) -> None:
        storage = FakeStorage()
        etl = ETLService(source=FakeSource(VALID_RECORDS), storage=storage)
        result = etl.run(filters={})
        amounts = {t.amount for t in result}
        assert amounts == {100.0, 250.0, 75.5}

    def test_quality_pipeline_on_valid_dataset_all_pass(self) -> None:
        rules = [
            NotNullRule(fields=["id", "amount", "currency", "account_id"]),
            PositiveAmountRule(),
            ValidCurrencyRule(),
            NoDuplicateRule(id_field="id"),
            DateRangeRule(
                min_date=datetime(2020, 1, 1),
                max_date=datetime(2030, 12, 31),
                date_field="timestamp",
            ),
        ]
        service = QualityService(rules=rules)
        results = service.validate(VALID_RECORDS)
        assert all(r.passed for r in results)

    def test_quality_pipeline_detects_negative_amount(self) -> None:
        rules = [PositiveAmountRule()]
        service = QualityService(rules=rules)
        bad_records = [{"id": "txn-001", "amount": -10.0}]
        results = service.validate(bad_records)
        assert results[0].passed is False

    def test_quality_pipeline_detects_invalid_currency(self) -> None:
        rules = [ValidCurrencyRule()]
        service = QualityService(rules=rules)
        bad_records = [{"currency": "XYZ"}]
        results = service.validate(bad_records)
        assert results[0].passed is False

    def test_quality_pipeline_detects_duplicates(self) -> None:
        rules = [NoDuplicateRule(id_field="id")]
        service = QualityService(rules=rules)
        dup_records = [{"id": "txn-001"}, {"id": "txn-001"}]
        results = service.validate(dup_records)
        assert results[0].passed is False

    def test_empty_dataset_produces_no_transactions(self) -> None:
        storage = FakeStorage()
        etl = ETLService(source=FakeSource([]), storage=storage)
        result = etl.run(filters={})
        assert result == []
        assert storage.saved == []
