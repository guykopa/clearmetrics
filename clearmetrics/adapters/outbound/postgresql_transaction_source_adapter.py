from typing import Any
from sqlalchemy.orm import Session

from clearmetrics.adapters.outbound.postgresql_models import TransactionRow
from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort


class PostgreSQLTransactionSourceAdapter(ITransactionSourcePort):
    """Fetches transaction records from a PostgreSQL database via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch_transactions(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch transactions matching the given filters."""
        query = self._session.query(TransactionRow)
        if account_id := filters.get("account_id"):
            query = query.filter(TransactionRow.account_id == account_id)
        return [
            {
                "id": row.id,
                "amount": row.amount,
                "currency": row.currency,
                "account_id": row.account_id,
                "timestamp": row.timestamp,
                "source": row.source,
            }
            for row in query.all()
        ]
