import pytest
from datetime import datetime
from clearmetrics.domain.models.metric import Metric
from clearmetrics.domain.models.report import Report


class TestReportCreation:
    def _make_metric(self, name: str = "revenue") -> Metric:
        return Metric(
            name=name,
            value=1000.0,
            unit="EUR",
            timestamp=datetime(2024, 1, 15),
            dimensions={},
        )

    def test_creates_valid_report(self) -> None:
        metric = self._make_metric()
        report = Report(
            id="rpt-001",
            title="Monthly Revenue",
            metrics=[metric],
            generated_at=datetime(2024, 1, 15, 12, 0),
            generated_by="usr-001",
        )
        assert report.id == "rpt-001"
        assert report.title == "Monthly Revenue"
        assert len(report.metrics) == 1
        assert report.generated_by == "usr-001"

    def test_report_is_immutable(self) -> None:
        report = Report(
            id="rpt-001",
            title="Report",
            metrics=[],
            generated_at=datetime(2024, 1, 15),
            generated_by="usr-001",
        )
        with pytest.raises(Exception):
            report.title = "Hacked"  # type: ignore[misc]

    def test_report_accepts_multiple_metrics(self) -> None:
        metrics = [self._make_metric(name=f"metric_{i}") for i in range(3)]
        report = Report(
            id="rpt-002",
            title="Full Report",
            metrics=metrics,
            generated_at=datetime(2024, 1, 15),
            generated_by="usr-001",
        )
        assert len(report.metrics) == 3

    def test_report_accepts_empty_metrics(self) -> None:
        report = Report(
            id="rpt-003",
            title="Empty Report",
            metrics=[],
            generated_at=datetime(2024, 1, 15),
            generated_by="usr-001",
        )
        assert report.metrics == []

    def test_raises_on_empty_id(self) -> None:
        with pytest.raises(ValueError):
            Report(
                id="",
                title="Report",
                metrics=[],
                generated_at=datetime(2024, 1, 15),
                generated_by="usr-001",
            )

    def test_raises_on_empty_title(self) -> None:
        with pytest.raises(ValueError):
            Report(
                id="rpt-004",
                title="",
                metrics=[],
                generated_at=datetime(2024, 1, 15),
                generated_by="usr-001",
            )

    def test_raises_on_empty_generated_by(self) -> None:
        with pytest.raises(ValueError):
            Report(
                id="rpt-005",
                title="Report",
                metrics=[],
                generated_at=datetime(2024, 1, 15),
                generated_by="",
            )
