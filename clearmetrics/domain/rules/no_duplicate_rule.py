from collections import Counter
from typing import Any

from clearmetrics.domain.models.quality_result import QualityResult
from clearmetrics.ports.outbound.i_quality_rule_port import IQualityRulePort


class NoDuplicateRule(IQualityRulePort):
    """Validates that no two records share the same value for the id field."""

    def __init__(self, id_field: str) -> None:
        self._id_field = id_field

    @property
    def rule_name(self) -> str:
        return "NoDuplicateRule"

    def validate(self, records: list[dict[str, Any]]) -> QualityResult:
        """Validate that every record has a unique value for the id field."""
        id_counts = Counter(record.get(self._id_field) for record in records)
        duplicate_ids = {id_val for id_val, count in id_counts.items() if count > 1}
        seen: set[Any] = set()
        failures = []
        for record in records:
            id_val = record.get(self._id_field)
            if id_val in duplicate_ids and id_val not in seen:
                seen.add(id_val)
                failures.append(record)
        passed = len(duplicate_ids) == 0
        return QualityResult(
            rule_name=self.rule_name,
            passed=passed,
            failed_count=len(duplicate_ids),
            error_samples=failures,
        )
