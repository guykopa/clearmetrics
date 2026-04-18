from typing import Any

from clearmetrics.domain.services.quality_service import QualityService
from clearmetrics.domain.models.quality_result import QualityResult
from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort


class AlwaysPassRule(IQualityRulePort):
    @property
    def rule_name(self) -> str:
        return "AlwaysPassRule"

    def validate(self, records: list[dict[str, Any]]) -> QualityResult:
        return QualityResult(rule_name=self.rule_name, passed=True, failed_count=0, error_samples=[])


class AlwaysFailRule(IQualityRulePort):
    @property
    def rule_name(self) -> str:
        return "AlwaysFailRule"

    def validate(self, records: list[dict[str, Any]]) -> QualityResult:
        return QualityResult(
            rule_name=self.rule_name,
            passed=False,
            failed_count=len(records) or 1,
            error_samples=records[:1],
        )


RECORDS = [{"id": "txn-001", "amount": 100.0, "currency": "EUR"}]


class TestQualityService:
    def test_returns_one_result_per_rule(self) -> None:
        service = QualityService(rules=[AlwaysPassRule(), AlwaysFailRule()])
        results = service.validate(RECORDS)
        assert len(results) == 2

    def test_returns_empty_list_when_no_rules(self) -> None:
        service = QualityService(rules=[])
        results = service.validate(RECORDS)
        assert results == []

    def test_all_pass_when_all_rules_pass(self) -> None:
        service = QualityService(rules=[AlwaysPassRule(), AlwaysPassRule()])
        results = service.validate(RECORDS)
        assert all(r.passed for r in results)

    def test_fail_when_one_rule_fails(self) -> None:
        service = QualityService(rules=[AlwaysPassRule(), AlwaysFailRule()])
        results = service.validate(RECORDS)
        assert any(not r.passed for r in results)

    def test_result_rule_names_match_rules(self) -> None:
        service = QualityService(rules=[AlwaysPassRule(), AlwaysFailRule()])
        results = service.validate(RECORDS)
        names = {r.rule_name for r in results}
        assert names == {"AlwaysPassRule", "AlwaysFailRule"}

    def test_passes_records_to_each_rule(self) -> None:
        received: list[list[dict[str, Any]]] = []

        class CapturingRule(IQualityRulePort):
            @property
            def rule_name(self) -> str:
                return "CapturingRule"

            def validate(self, records: list[dict[str, Any]]) -> QualityResult:
                received.append(records)
                return QualityResult(rule_name=self.rule_name, passed=True, failed_count=0, error_samples=[])

        service = QualityService(rules=[CapturingRule()])
        service.validate(RECORDS)
        assert received[0] == RECORDS

    def test_service_depends_on_port(self) -> None:
        rule = AlwaysPassRule()
        service = QualityService(rules=[rule])
        assert all(isinstance(r, IQualityRulePort) for r in service._rules)
