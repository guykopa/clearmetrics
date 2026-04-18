from abc import ABC, abstractmethod
from typing import Any


class IMetricSourcePort(ABC):
    """Abstract port for reading raw metric records from any source."""

    @abstractmethod
    def fetch_metrics(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch raw metric records matching the given filters."""
