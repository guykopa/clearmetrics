from abc import ABC, abstractmethod
from typing import Any


class IQualityRulePort(ABC):
    """Abstract port for a single data quality validation rule."""

    @abstractmethod
    def validate(self, records: list[dict[str, Any]]) -> "QualityResult":  # type: ignore[name-defined]
        """Validate records and return a QualityResult."""

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Return the unique name of this rule."""
