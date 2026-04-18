from abc import ABC, abstractmethod
from typing import Any


class ITransactionSourcePort(ABC):
    """Abstract port for reading raw transaction records from any source."""

    @abstractmethod
    def fetch_transactions(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch raw transaction records matching the given filters."""
