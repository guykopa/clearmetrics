from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Metric:
    """Immutable domain model representing a single business metric."""

    name: str
    value: float
    unit: str
    timestamp: datetime
    dimensions: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Metric name must not be empty.")
        if not self.unit:
            raise ValueError("Metric unit must not be empty.")
        if self.value < 0:
            raise ValueError(f"Metric value must be >= 0, got {self.value}.")
