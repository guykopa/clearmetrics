import pytest
from datetime import datetime
from clearmetrics.domain.models.transaction import Transaction
from clearmetrics.domain.exceptions import InvalidAmountError, InvalidCurrencyError


class TestTransactionCreation:
    def test_creates_valid_transaction(self) -> None:
        txn = Transaction(
            id="txn-001",
            amount=150.75,
            currency="EUR",
            account_id="acc-001",
            timestamp=datetime(2024, 1, 15, 10, 30),
            source="postgresql",
        )
        assert txn.id == "txn-001"
        assert txn.amount == 150.75
        assert txn.currency == "EUR"
        assert txn.account_id == "acc-001"
        assert txn.source == "postgresql"

    def test_transaction_is_immutable(self) -> None:
        txn = Transaction(
            id="txn-001",
            amount=100.0,
            currency="USD",
            account_id="acc-001",
            timestamp=datetime(2024, 1, 15),
            source="csv",
        )
        with pytest.raises(Exception):
            txn.amount = 999.0  # type: ignore[misc]

    def test_raises_on_zero_amount(self) -> None:
        with pytest.raises(InvalidAmountError):
            Transaction(
                id="txn-002",
                amount=0.0,
                currency="EUR",
                account_id="acc-001",
                timestamp=datetime(2024, 1, 15),
                source="postgresql",
            )

    def test_raises_on_negative_amount(self) -> None:
        with pytest.raises(InvalidAmountError):
            Transaction(
                id="txn-003",
                amount=-50.0,
                currency="EUR",
                account_id="acc-001",
                timestamp=datetime(2024, 1, 15),
                source="postgresql",
            )

    def test_raises_on_invalid_currency(self) -> None:
        with pytest.raises(InvalidCurrencyError):
            Transaction(
                id="txn-004",
                amount=100.0,
                currency="INVALID",
                account_id="acc-001",
                timestamp=datetime(2024, 1, 15),
                source="postgresql",
            )

    def test_raises_on_empty_id(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                id="",
                amount=100.0,
                currency="EUR",
                account_id="acc-001",
                timestamp=datetime(2024, 1, 15),
                source="postgresql",
            )

    def test_raises_on_empty_account_id(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                id="txn-005",
                amount=100.0,
                currency="EUR",
                account_id="",
                timestamp=datetime(2024, 1, 15),
                source="postgresql",
            )

    def test_valid_sources(self) -> None:
        for source in ("postgresql", "csv", "external_api"):
            txn = Transaction(
                id="txn-006",
                amount=100.0,
                currency="USD",
                account_id="acc-001",
                timestamp=datetime(2024, 1, 15),
                source=source,
            )
            assert txn.source == source

    def test_raises_on_invalid_source(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                id="txn-007",
                amount=100.0,
                currency="USD",
                account_id="acc-001",
                timestamp=datetime(2024, 1, 15),
                source="unknown",
            )
