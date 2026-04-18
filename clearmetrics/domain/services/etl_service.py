import logging
from typing import Any

from clearmetrics.domain.exceptions import DomainException
from clearmetrics.domain.models.transaction import Transaction
from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort
from clearmetrics.ports.outbound.i_transaction_storage_port import ITransactionStoragePort

logger = logging.getLogger(__name__)


class ETLService:
    """Extracts raw transaction records, transforms them to domain objects, and persists them."""

    def __init__(self, source: ITransactionSourcePort, storage: ITransactionStoragePort) -> None:
        self._source = source
        self._storage = storage

    def run(self, filters: dict[str, Any]) -> list[Transaction]:
        """Run the ETL pipeline and return successfully transformed transactions."""
        raw_records = self._source.fetch_transactions(filters)
        transactions = []
        for record in raw_records:
            try:
                transaction = Transaction(
                    id=record["id"],
                    amount=record["amount"],
                    currency=record["currency"],
                    account_id=record["account_id"],
                    timestamp=record["timestamp"],
                    source=record["source"],
                )
                self._storage.save_transaction(record)
                transactions.append(transaction)
            except (DomainException, ValueError, KeyError) as exc:
                logger.warning("Skipping invalid record %s: %s", record.get("id"), exc)
        return transactions
