from abc import ABC, abstractmethod
from typing import Any


class ITransactionStoragePort(ABC):
    """Abstract port for persisting transaction records."""

    @abstractmethod
    def save_transaction(self, transaction: dict[str, Any]) -> None:
        """Persist a single transaction record."""
