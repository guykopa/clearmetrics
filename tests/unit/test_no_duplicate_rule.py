from clearmetrics.domain.rules.no_duplicate_rule import NoDuplicateRule
from clearmetrics.domain.models.quality_result import QualityResult


class TestNoDuplicateRule:
    def test_rule_name(self) -> None:
        rule = NoDuplicateRule(id_field="id")
        assert rule.rule_name == "NoDuplicateRule"

    def test_passes_when_no_duplicates(self) -> None:
        rule = NoDuplicateRule(id_field="id")
        records = [
            {"id": "txn-001", "amount": 100.0},
            {"id": "txn-002", "amount": 200.0},
        ]
        result = rule.validate(records)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_when_duplicate_ids(self) -> None:
        rule = NoDuplicateRule(id_field="id")
        records = [
            {"id": "txn-001", "amount": 100.0},
            {"id": "txn-001", "amount": 200.0},
        ]
        result = rule.validate(records)
        assert result.passed is False
        assert result.failed_count == 1

    def test_counts_multiple_duplicate_groups(self) -> None:
        rule = NoDuplicateRule(id_field="id")
        records = [
            {"id": "txn-001"},
            {"id": "txn-001"},
            {"id": "txn-002"},
            {"id": "txn-002"},
            {"id": "txn-003"},
        ]
        result = rule.validate(records)
        assert result.failed_count == 2

    def test_error_samples_contain_duplicate_ids(self) -> None:
        rule = NoDuplicateRule(id_field="id")
        records = [
            {"id": "txn-001"},
            {"id": "txn-001"},
        ]
        result = rule.validate(records)
        assert any(s["id"] == "txn-001" for s in result.error_samples)

    def test_fails_when_id_field_missing(self) -> None:
        rule = NoDuplicateRule(id_field="id")
        records = [{"amount": 100.0}, {"amount": 200.0}]
        result = rule.validate(records)
        assert result.passed is False

    def test_passes_on_empty_records(self) -> None:
        rule = NoDuplicateRule(id_field="id")
        result = rule.validate([])
        assert result.passed is True

    def test_passes_on_single_record(self) -> None:
        rule = NoDuplicateRule(id_field="id")
        result = rule.validate([{"id": "txn-001"}])
        assert result.passed is True

    def test_implements_quality_rule_port(self) -> None:
        from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort
        assert isinstance(NoDuplicateRule(id_field="id"), IQualityRulePort)
