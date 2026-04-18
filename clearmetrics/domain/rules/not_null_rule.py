from typing import Any

from clearmetrics.domain.models.quality_result import QualityResult
from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort


class NotNullRule(IQualityRulePort):
    """Validates that required fields are not null or missing in every record."""

    def __init__(self, fields: list[str]) -> None:
        self._fields = fields

    @property
    def rule_name(self) -> str:
        return "NotNullRule"

    def validate(self, records: list[dict[str, Any]]) -> QualityResult:
        """Validate that none of the required fields are null or absent."""
        failures = [
            record for record in records
            if any(record.get(field) is None for field in self._fields)
        ]
        passed = len(failures) == 0
        return QualityResult(
            rule_name=self.rule_name,
            passed=passed,
            failed_count=len(failures),
            error_samples=failures,
        )
