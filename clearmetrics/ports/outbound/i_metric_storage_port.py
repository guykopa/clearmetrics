from abc import ABC, abstractmethod
from typing import Any


class IMetricStoragePort(ABC):
    """Abstract port for persisting metric records."""

    @abstractmethod
    def save_metric(self, metric: dict[str, Any]) -> None:
        """Persist a single metric record."""
