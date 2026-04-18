import pytest
from clearmetrics.domain.rules.not_null_rule import NotNullRule
from clearmetrics.domain.models.quality_result import QualityResult


class TestNotNullRule:
    def test_rule_name(self) -> None:
        rule = NotNullRule(fields=["amount", "currency"])
        assert rule.rule_name == "NotNullRule"

    def test_passes_when_no_nulls(self) -> None:
        rule = NotNullRule(fields=["amount", "currency"])
        records = [
            {"amount": 100.0, "currency": "EUR"},
            {"amount": 200.0, "currency": "USD"},
        ]
        result = rule.validate(records)
        assert isinstance(result, QualityResult)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_when_field_is_none(self) -> None:
        rule = NotNullRule(fields=["amount", "currency"])
        records = [
            {"amount": None, "currency": "EUR"},
            {"amount": 200.0, "currency": "USD"},
        ]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_fails_when_field_is_missing(self) -> None:
        rule = NotNullRule(fields=["amount", "currency"])
        records = [
            {"currency": "EUR"},
        ]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_counts_multiple_failures(self) -> None:
        rule = NotNullRule(fields=["amount"])
        records = [
            {"amount": None},
            {"amount": None},
            {"amount": 100.0},
        ]
        result = rule.validate(records)
        assert result.failed_count == 2

    def test_error_samples_contain_failing_records(self) -> None:
        rule = NotNullRule(fields=["amount"])
        records = [{"amount": None, "id": "txn-001"}]
        result = rule.validate(records)
        assert len(result.error_samples) == 1
        assert result.error_samples[0]["id"] == "txn-001"

    def test_passes_on_empty_records(self) -> None:
        rule = NotNullRule(fields=["amount"])
        result = rule.validate([])
        assert result.passed is True
        assert result.failed_count == 0

    def test_implements_quality_rule_port(self) -> None:
        from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort
        rule = NotNullRule(fields=["amount"])
        assert isinstance(rule, IQualityRulePort)
