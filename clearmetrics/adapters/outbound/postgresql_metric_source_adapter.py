from typing import Any
from sqlalchemy.orm import Session

from clearmetrics.adapters.outbound.postgresql_models import MetricRow
from clearmetrics.ports.outbound.i_metric_source_port import IMetricSourcePort


class PostgreSQLMetricSourceAdapter(IMetricSourcePort):
    """Fetches metric records from a PostgreSQL database via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch_metrics(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch metrics matching the given filters."""
        query = self._session.query(MetricRow)
        if name := filters.get("name"):
            query = query.filter(MetricRow.name == name)
        return [
            {
                "name": row.name,
                "value": row.value,
                "unit": row.unit,
                "timestamp": row.timestamp,
                "dimensions": row.dimensions or {},
            }
            for row in query.all()
        ]
