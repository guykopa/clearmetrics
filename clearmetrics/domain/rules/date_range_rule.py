from datetime import datetime
from typing import Any

from clearmetrics.domain.models.quality_result import QualityResult
from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort


class DateRangeRule(IQualityRulePort):
    """Validates that every record's date field falls within an acceptable range."""

    def __init__(self, min_date: datetime, max_date: datetime, date_field: str) -> None:
        self._min_date = min_date
        self._max_date = max_date
        self._date_field = date_field

    @property
    def rule_name(self) -> str:
        return "DateRangeRule"

    def validate(self, records: list[dict[str, Any]]) -> QualityResult:
        """Validate that date_field is present and within [min_date, max_date]."""
        failures = [
            record for record in records
            if not isinstance(record.get(self._date_field), datetime)
            or not (self._min_date <= record[self._date_field] <= self._max_date)
        ]
        passed = len(failures) == 0
        return QualityResult(
            rule_name=self.rule_name,
            passed=passed,
            failed_count=len(failures),
            error_samples=failures,
        )
