from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QualityResult:
    """Immutable domain model representing the outcome of a quality rule validation."""

    rule_name: str
    passed: bool
    failed_count: int
    error_samples: list[dict[str, Any]]

    def __post_init__(self) -> None:
        if not self.rule_name:
            raise ValueError("QualityResult rule_name must not be empty.")
        if self.failed_count < 0:
            raise ValueError(f"failed_count must be >= 0, got {self.failed_count}.")
        if self.passed and self.failed_count != 0:
            raise ValueError("passed=True is inconsistent with failed_count > 0.")
        if not self.passed and self.failed_count == 0:
            raise ValueError("passed=False is inconsistent with failed_count == 0.")
