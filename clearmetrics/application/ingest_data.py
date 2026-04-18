from typing import Any

from clearmetrics.domain.models.transaction import Transaction
from clearmetrics.domain.services.etl_service import ETLService

_ALLOWED_ROLES = frozenset({"admin", "analyst"})


class IngestDataUseCase:
    """Orchestrates the ETL pipeline after verifying the user has ingestion rights."""

    def __init__(self, etl_service: ETLService) -> None:
        self._etl_service = etl_service

    def execute(self, filters: dict[str, Any], user_role: str) -> list[Transaction]:
        """Run the ingestion pipeline for an authorized user."""
        if user_role not in _ALLOWED_ROLES:
            raise PermissionError(f"Role '{user_role}' is not allowed to ingest data.")
        return self._etl_service.run(filters=filters)
