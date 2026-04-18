from typing import Any
from sqlalchemy.orm import Session

from clearmetrics.adapters.outbound.postgresql_models import TransactionRow
from clearmetrics.ports.outbound.i_transaction_storage_port import (
    ITransactionStoragePort,
)


class PostgreSQLTransactionStorageAdapter(ITransactionStoragePort):
    """Persists transaction records to a PostgreSQL database via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save_transaction(self, transaction: dict[str, Any]) -> None:
        """Persist a single transaction record."""
        row = TransactionRow(
            id=transaction["id"],
            amount=transaction["amount"],
            currency=transaction["currency"],
            account_id=transaction["account_id"],
            timestamp=transaction["timestamp"],
            source=transaction["source"],
        )
        self._session.merge(row)
