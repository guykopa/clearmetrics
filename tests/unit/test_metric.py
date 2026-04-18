import pytest
from datetime import datetime
from clearmetrics.domain.models.metric import Metric


class TestMetricCreation:
    def test_creates_valid_metric(self) -> None:
        metric = Metric(
            name="revenue",
            value=10000.0,
            unit="EUR",
            timestamp=datetime(2024, 1, 15, 10, 30),
            dimensions={"region": "EU", "product": "A"},
        )
        assert metric.name == "revenue"
        assert metric.value == 10000.0
        assert metric.unit == "EUR"
        assert metric.dimensions == {"region": "EU", "product": "A"}

    def test_metric_is_immutable(self) -> None:
        metric = Metric(
            name="revenue",
            value=100.0,
            unit="EUR",
            timestamp=datetime(2024, 1, 15),
            dimensions={},
        )
        with pytest.raises(Exception):
            metric.value = 999.0  # type: ignore[misc]

    def test_creates_metric_with_empty_dimensions(self) -> None:
        metric = Metric(
            name="latency",
            value=42.5,
            unit="ms",
            timestamp=datetime(2024, 1, 15),
            dimensions={},
        )
        assert metric.dimensions == {}

    def test_raises_on_empty_name(self) -> None:
        with pytest.raises(ValueError):
            Metric(
                name="",
                value=100.0,
                unit="EUR",
                timestamp=datetime(2024, 1, 15),
                dimensions={},
            )

    def test_raises_on_empty_unit(self) -> None:
        with pytest.raises(ValueError):
            Metric(
                name="revenue",
                value=100.0,
                unit="",
                timestamp=datetime(2024, 1, 15),
                dimensions={},
            )

    def test_raises_on_negative_value(self) -> None:
        with pytest.raises(ValueError):
            Metric(
                name="revenue",
                value=-1.0,
                unit="EUR",
                timestamp=datetime(2024, 1, 15),
                dimensions={},
            )

    def test_zero_value_is_valid(self) -> None:
        metric = Metric(
            name="errors",
            value=0.0,
            unit="count",
            timestamp=datetime(2024, 1, 15),
            dimensions={},
        )
        assert metric.value == 0.0
