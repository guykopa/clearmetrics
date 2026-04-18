from clearmetrics.domain.rules.valid_currency_rule import ValidCurrencyRule
from clearmetrics.domain.models.quality_result import QualityResult


class TestValidCurrencyRule:
    def test_rule_name(self) -> None:
        rule = ValidCurrencyRule()
        assert rule.rule_name == "ValidCurrencyRule"

    def test_passes_when_all_currencies_valid(self) -> None:
        rule = ValidCurrencyRule()
        records = [
            {"currency": "EUR"},
            {"currency": "USD"},
            {"currency": "GBP"},
        ]
        result = rule.validate(records)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_when_currency_invalid(self) -> None:
        rule = ValidCurrencyRule()
        records = [{"currency": "INVALID"}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_fails_when_currency_missing(self) -> None:
        rule = ValidCurrencyRule()
        records = [{"amount": 100.0}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_fails_when_currency_empty_string(self) -> None:
        rule = ValidCurrencyRule()
        records = [{"currency": ""}]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_counts_multiple_failures(self) -> None:
        rule = ValidCurrencyRule()
        records = [
            {"currency": "EUR"},
            {"currency": "XYZ"},
            {"currency": "ABC"},
        ]
        result = rule.validate(records)
        assert result.failed_count == 2

    def test_error_samples_contain_failing_records(self) -> None:
        rule = ValidCurrencyRule()
        records = [{"currency": "FAKE", "id": "txn-001"}]
        result = rule.validate(records)
        assert result.error_samples[0]["id"] == "txn-001"

    def test_passes_on_empty_records(self) -> None:
        rule = ValidCurrencyRule()
        result = rule.validate([])
        assert result.passed is True

    def test_implements_quality_rule_port(self) -> None:
        from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort
        assert isinstance(ValidCurrencyRule(), IQualityRulePort)
