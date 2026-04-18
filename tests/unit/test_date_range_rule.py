from datetime import datetime
from clearmetrics.domain.rules.date_range_rule import DateRangeRule


class TestDateRangeRule:
    def test_rule_name(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        assert rule.rule_name == "DateRangeRule"

    def test_passes_when_all_dates_in_range(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        records = [
            {"timestamp": datetime(2023, 6, 15)},
            {"timestamp": datetime(2024, 1, 1)},
        ]
        result = rule.validate(records)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_when_date_before_min(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        records = [{"timestamp": datetime(2019, 12, 31)}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_fails_when_date_after_max(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        records = [{"timestamp": datetime(2026, 1, 1)}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_passes_on_boundary_dates(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        records = [
            {"timestamp": datetime(2020, 1, 1)},
            {"timestamp": datetime(2025, 12, 31)},
        ]
        result = rule.validate(records)
        assert result.passed is True

    def test_fails_when_date_field_missing(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        records = [{"amount": 100.0}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_counts_multiple_failures(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        records = [
            {"timestamp": datetime(2019, 1, 1)},
            {"timestamp": datetime(2026, 1, 1)},
            {"timestamp": datetime(2023, 1, 1)},
        ]
        result = rule.validate(records)
        assert result.failed_count == 2

    def test_error_samples_contain_failing_records(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        records = [{"timestamp": datetime(2019, 1, 1), "id": "txn-001"}]
        result = rule.validate(records)
        assert result.error_samples[0]["id"] == "txn-001"

    def test_passes_on_empty_records(self) -> None:
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        result = rule.validate([])
        assert result.passed is True

    def test_implements_quality_rule_port(self) -> None:
        from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort
        rule = DateRangeRule(
            min_date=datetime(2020, 1, 1),
            max_date=datetime(2025, 12, 31),
            date_field="timestamp",
        )
        assert isinstance(rule, IQualityRulePort)
