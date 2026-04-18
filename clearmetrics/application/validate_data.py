from typing import Any

from clearmetrics.domain.models.quality_result import QualityResult
from clearmetrics.domain.services.quality_service import QualityService

_ALLOWED_ROLES = frozenset({"admin", "analyst"})


class ValidateDataUseCase:
    """Orchestrates data quality validation after verifying user rights."""

    def __init__(self, quality_service: QualityService) -> None:
        self._quality_service = quality_service

    def execute(
        self, records: list[dict[str, Any]], user_role: str
    ) -> list[QualityResult]:
        """Run all quality rules against records for an authorized user."""
        if user_role not in _ALLOWED_ROLES:
            raise PermissionError(
                f"Role '{user_role}' is not allowed to validate data."
            )
        return self._quality_service.validate(records)
