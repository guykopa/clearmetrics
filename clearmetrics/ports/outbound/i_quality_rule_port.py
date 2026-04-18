from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from clearmetrics.domain.models.quality_result import QualityResult


class IQualityRulePort(ABC):
    """Abstract port for a single data quality validation rule."""

    @abstractmethod
    def validate(self, records: list[dict[str, Any]]) -> "QualityResult":
        """Validate records and return a QualityResult."""

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Return the unique name of this rule."""
