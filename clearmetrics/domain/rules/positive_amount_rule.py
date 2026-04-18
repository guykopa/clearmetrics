from typing import Any

from clearmetrics.domain.models.quality_result import QualityResult
from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort


class PositiveAmountRule(IQualityRulePort):
    """Validates that every record has an amount strictly greater than zero."""

    @property
    def rule_name(self) -> str:
        return "PositiveAmountRule"

    def validate(self, records: list[dict[str, Any]]) -> QualityResult:
        """Validate that amount is present and strictly positive in every record."""
        failures = [
            record for record in records
            if not isinstance(record.get("amount"), (int, float))
            or record["amount"] <= 0
        ]
        passed = len(failures) == 0
        return QualityResult(
            rule_name=self.rule_name,
            passed=passed,
            failed_count=len(failures),
            error_samples=failures,
        )
