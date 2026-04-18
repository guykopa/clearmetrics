import pytest
from clearmetrics.domain.rules.positive_amount_rule import PositiveAmountRule
from clearmetrics.domain.models.quality_result import QualityResult


class TestPositiveAmountRule:
    def test_rule_name(self) -> None:
        rule = PositiveAmountRule()
        assert rule.rule_name == "PositiveAmountRule"

    def test_passes_when_all_amounts_positive(self) -> None:
        rule = PositiveAmountRule()
        records = [
            {"amount": 100.0},
            {"amount": 0.01},
        ]
        result = rule.validate(records)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_when_amount_is_zero(self) -> None:
        rule = PositiveAmountRule()
        records = [{"amount": 0.0}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_fails_when_amount_is_negative(self) -> None:
        rule = PositiveAmountRule()
        records = [{"amount": -50.0}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_fails_when_amount_is_missing(self) -> None:
        rule = PositiveAmountRule()
        records = [{"currency": "EUR"}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_counts_multiple_failures(self) -> None:
        rule = PositiveAmountRule()
        records = [
            {"amount": -10.0},
            {"amount": 0.0},
            {"amount": 100.0},
        ]
        result = rule.validate(records)
        assert result.failed_count == 2

    def test_error_samples_contain_failing_records(self) -> None:
        rule = PositiveAmountRule()
        records = [{"amount": -5.0, "id": "txn-001"}]
        result = rule.validate(records)
        assert result.error_samples[0]["id"] == "txn-001"

    def test_passes_on_empty_records(self) -> None:
        rule = PositiveAmountRule()
        result = rule.validate([])
        assert result.passed is True

    def test_implements_quality_rule_port(self) -> None:
        from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort
        assert isinstance(PositiveAmountRule(), IQualityRulePort)
