from typing import Any

from clearmetrics.domain.models.quality_result import QualityResult
from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort


class QualityService:
    """Runs all registered quality rules against a dataset and collects results."""

    def __init__(self, rules: list[IQualityRulePort]) -> None:
        self._rules = rules

    def validate(self, records: list[dict[str, Any]]) -> list[QualityResult]:
        """Apply every rule to the records and return one QualityResult per rule."""
        return [rule.validate(records) for rule in self._rules]
