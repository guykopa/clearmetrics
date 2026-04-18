import logging
from typing import Any

from clearmetrics.domain.exceptions import DomainException
from clearmetrics.domain.models.metric import Metric
from clearmetrics.ports.outbound.i_metric_source_port import IMetricSourcePort

logger = logging.getLogger(__name__)

_ALLOWED_ROLES = frozenset({"admin", "analyst", "viewer"})


class ExportMetricsUseCase:
    """Fetches and returns Metric objects for authorized users."""

    def __init__(self, source: IMetricSourcePort) -> None:
        self._source = source

    def execute(self, filters: dict[str, Any], user_role: str) -> list[Metric]:
        """Return metrics matching filters for an authorized user."""
        if user_role not in _ALLOWED_ROLES:
            raise PermissionError(f"Role '{user_role}' is not allowed to export metrics.")
        raw_records = self._source.fetch_metrics(filters)
        metrics = []
        for record in raw_records:
            try:
                metrics.append(Metric(
                    name=record["name"],
                    value=record["value"],
                    unit=record["unit"],
                    timestamp=record["timestamp"],
                    dimensions=record.get("dimensions", {}),
                ))
            except (DomainException, ValueError, KeyError) as exc:
                logger.warning("Skipping invalid metric record: %s", exc)
        return metrics
