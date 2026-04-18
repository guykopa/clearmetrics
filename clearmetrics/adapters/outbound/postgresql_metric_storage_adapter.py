from typing import Any
from sqlalchemy.orm import Session

from clearmetrics.adapters.outbound.postgresql_models import MetricRow
from clearmetrics.ports.outbound.i_metric_storage_port import IMetricStoragePort


class PostgreSQLMetricStorageAdapter(IMetricStoragePort):
    """Persists metric records to a PostgreSQL database via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save_metric(self, metric: dict[str, Any]) -> None:
        """Persist a single metric record."""
        row = MetricRow(
            name=metric["name"],
            value=metric["value"],
            unit=metric["unit"],
            timestamp=metric["timestamp"],
            dimensions=metric.get("dimensions"),
        )
        self._session.add(row)
