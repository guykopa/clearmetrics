import pytest
from typing import Any

from clearmetrics.application.validate_data import ValidateDataUseCase
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


@pytest.fixture
def passing_use_case() -> ValidateDataUseCase:
    service = QualityService(rules=[AlwaysPassRule()])
    return ValidateDataUseCase(quality_service=service)


@pytest.fixture
def failing_use_case() -> ValidateDataUseCase:
    service = QualityService(rules=[AlwaysPassRule(), AlwaysFailRule()])
    return ValidateDataUseCase(quality_service=service)


class TestValidateDataUseCase:
    def test_admin_can_validate(self, passing_use_case: ValidateDataUseCase) -> None:
        results = passing_use_case.execute(records=RECORDS, user_role="admin")
        assert len(results) == 1

    def test_analyst_can_validate(self, passing_use_case: ValidateDataUseCase) -> None:
        results = passing_use_case.execute(records=RECORDS, user_role="analyst")
        assert len(results) == 1

    def test_viewer_cannot_validate(self, passing_use_case: ValidateDataUseCase) -> None:
        with pytest.raises(PermissionError):
            passing_use_case.execute(records=RECORDS, user_role="viewer")

    def test_unknown_role_cannot_validate(self, passing_use_case: ValidateDataUseCase) -> None:
        with pytest.raises(PermissionError):
            passing_use_case.execute(records=RECORDS, user_role="unknown")

    def test_returns_one_result_per_rule(self, failing_use_case: ValidateDataUseCase) -> None:
        results = failing_use_case.execute(records=RECORDS, user_role="admin")
        assert len(results) == 2

    def test_returns_quality_result_objects(self, passing_use_case: ValidateDataUseCase) -> None:
        results = passing_use_case.execute(records=RECORDS, user_role="admin")
        assert all(isinstance(r, QualityResult) for r in results)

    def test_returns_empty_when_no_rules(self) -> None:
        use_case = ValidateDataUseCase(quality_service=QualityService(rules=[]))
        results = use_case.execute(records=RECORDS, user_role="admin")
        assert results == []

    def test_all_passed_when_all_rules_pass(self, passing_use_case: ValidateDataUseCase) -> None:
        results = passing_use_case.execute(records=RECORDS, user_role="admin")
        assert all(r.passed for r in results)

    def test_detects_failures(self, failing_use_case: ValidateDataUseCase) -> None:
        results = failing_use_case.execute(records=RECORDS, user_role="admin")
        assert any(not r.passed for r in results)
