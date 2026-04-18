import pytest
from datetime import datetime
from typing import Any

from clearmetrics.application.export_metrics import ExportMetricsUseCase
from clearmetrics.domain.models.metric import Metric
from clearmetrics.ports.outbound.i_metric_source_port import IMetricSourcePort


class FakeMetricSource(IMetricSourcePort):
    def __init__(self, records: list[dict[str, Any]]) -> None:
        self._records = records

    def fetch_metrics(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        return self._records


RAW_METRIC = {
    "name": "revenue",
    "value": 10000.0,
    "unit": "EUR",
    "timestamp": datetime(2024, 1, 15, 10, 30),
    "dimensions": {"region": "EU"},
}


@pytest.fixture
def use_case() -> ExportMetricsUseCase:
    return ExportMetricsUseCase(source=FakeMetricSource([RAW_METRIC]))


class TestExportMetricsUseCase:
    def test_admin_can_export(self, use_case: ExportMetricsUseCase) -> None:
        result = use_case.execute(filters={}, user_role="admin")
        assert len(result) == 1
        assert isinstance(result[0], Metric)

    def test_analyst_can_export(self, use_case: ExportMetricsUseCase) -> None:
        result = use_case.execute(filters={}, user_role="analyst")
        assert len(result) == 1

    def test_viewer_can_export(self, use_case: ExportMetricsUseCase) -> None:
        result = use_case.execute(filters={}, user_role="viewer")
        assert len(result) == 1

    def test_unknown_role_cannot_export(self, use_case: ExportMetricsUseCase) -> None:
        with pytest.raises(PermissionError):
            use_case.execute(filters={}, user_role="unknown")

    def test_returns_metric_objects(self, use_case: ExportMetricsUseCase) -> None:
        result = use_case.execute(filters={}, user_role="admin")
        metric = result[0]
        assert metric.name == "revenue"
        assert metric.value == 10000.0
        assert metric.unit == "EUR"

    def test_returns_empty_on_no_records(self) -> None:
        use_case = ExportMetricsUseCase(source=FakeMetricSource([]))
        result = use_case.execute(filters={}, user_role="admin")
        assert result == []

    def test_passes_filters_to_source(self) -> None:
        received: list[dict[str, Any]] = []

        class CapturingSource(IMetricSourcePort):
            def fetch_metrics(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
                received.append(filters)
                return []

        use_case = ExportMetricsUseCase(source=CapturingSource())
        use_case.execute(filters={"name": "revenue"}, user_role="admin")
        assert received[0] == {"name": "revenue"}

    def test_skips_invalid_metric_records(self) -> None:
        invalid = {**RAW_METRIC, "value": -1.0}
        use_case = ExportMetricsUseCase(source=FakeMetricSource([RAW_METRIC, invalid]))
        result = use_case.execute(filters={}, user_role="admin")
        assert len(result) == 1
