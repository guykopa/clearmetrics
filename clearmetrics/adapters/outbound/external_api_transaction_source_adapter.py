from datetime import datetime
from typing import Any

import httpx

from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort


class ExternalAPITransactionSourceAdapter(ITransactionSourcePort):
    """Fetches transaction records from an external REST API via httpx."""

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def fetch_transactions(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch transactions from the external API, passing filters as query params."""
        response = self._client.get(
            f"{self._base_url}/transactions",
            params=filters,
        )
        response.raise_for_status()
        records = response.json()
        return [
            {**record, "timestamp": datetime.fromisoformat(record["timestamp"])}
            for record in records
        ]
