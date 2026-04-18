from dataclasses import dataclass
from datetime import datetime

from clearmetrics.domain.models.metric import Metric


@dataclass(frozen=True)
class Report:
    """Immutable domain model representing a generated analytics report."""

    id: str
    title: str
    metrics: list[Metric]
    generated_at: datetime
    generated_by: str

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Report id must not be empty.")
        if not self.title:
            raise ValueError("Report title must not be empty.")
        if not self.generated_by:
            raise ValueError("Report generated_by must not be empty.")
