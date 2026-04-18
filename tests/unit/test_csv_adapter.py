import pytest
from pathlib import Path
from datetime import datetime

from clearmetrics.adapters.outbound.csv_transaction_source_adapter import CSVTransactionSourceAdapter
from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort

CSV_CONTENT = """id,amount,currency,account_id,timestamp,source
txn-001,150.75,EUR,acc-001,2024-01-15 10:30:00,csv
txn-002,200.00,USD,acc-002,2024-01-16 09:00:00,csv
txn-003,50.50,GBP,acc-001,2024-01-17 14:00:00,csv
"""


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    path = tmp_path / "transactions.csv"
    path.write_text(CSV_CONTENT)
    return path


class TestCSVTransactionSourceAdapter:
    def test_implements_port(self, csv_file: Path) -> None:
        adapter = CSVTransactionSourceAdapter(file_path=csv_file)
        assert isinstance(adapter, ITransactionSourcePort)

    def test_fetch_returns_all_records(self, csv_file: Path) -> None:
        adapter = CSVTransactionSourceAdapter(file_path=csv_file)
        result = adapter.fetch_transactions(filters={})
        assert len(result) == 3

    def test_fetch_returns_correct_fields(self, csv_file: Path) -> None:
        adapter = CSVTransactionSourceAdapter(file_path=csv_file)
        record = adapter.fetch_transactions(filters={})[0]
        assert record["id"] == "txn-001"
        assert record["amount"] == 150.75
        assert record["currency"] == "EUR"
        assert record["account_id"] == "acc-001"
        assert record["source"] == "csv"

    def test_fetch_timestamp_is_datetime(self, csv_file: Path) -> None:
        adapter = CSVTransactionSourceAdapter(file_path=csv_file)
        record = adapter.fetch_transactions(filters={})[0]
        assert isinstance(record["timestamp"], datetime)

    def test_fetch_filters_by_account_id(self, csv_file: Path) -> None:
        adapter = CSVTransactionSourceAdapter(file_path=csv_file)
        result = adapter.fetch_transactions(filters={"account_id": "acc-001"})
        assert len(result) == 2
        assert all(r["account_id"] == "acc-001" for r in result)

    def test_fetch_returns_empty_on_no_match(self, csv_file: Path) -> None:
        adapter = CSVTransactionSourceAdapter(file_path=csv_file)
        result = adapter.fetch_transactions(filters={"account_id": "acc-999"})
        assert result == []

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        adapter = CSVTransactionSourceAdapter(file_path=tmp_path / "missing.csv")
        with pytest.raises(FileNotFoundError):
            adapter.fetch_transactions(filters={})
