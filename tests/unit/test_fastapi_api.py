import pytest
from datetime import datetime
from typing import Any
from fastapi.testclient import TestClient

from clearmetrics.adapters.inbound.fastapi_api import create_app
from clearmetrics.application.ingest_data import IngestDataUseCase
from clearmetrics.application.validate_data import ValidateDataUseCase
from clearmetrics.application.export_metrics import ExportMetricsUseCase
from clearmetrics.domain.models.transaction import Transaction
from clearmetrics.domain.models.metric import Metric
from clearmetrics.domain.models.quality_result import QualityResult
from clearmetrics.domain.services.auth_service import AuthService
from clearmetrics.ports.outbound.i_token_generator_port import ITokenGeneratorPort
from clearmetrics.ports.outbound.i_token_verifier_port import ITokenVerifierPort


class FakeTokenGenerator(ITokenGeneratorPort):
    def generate_token(self, user_id: str, role: str) -> str:
        return f"token-{user_id}-{role}"


class FakeTokenVerifier(ITokenVerifierPort):
    def verify_token(self, token: str) -> dict[str, str]:
        if token.startswith("token-"):
            parts = token[len("token-"):].rsplit("-", 1)
            return {"user_id": parts[0], "role": parts[1]}
        raise ValueError("Invalid token")


TRANSACTION = Transaction(
    id="txn-001", amount=100.0, currency="EUR",
    account_id="acc-001", timestamp=datetime(2024, 1, 15), source="postgresql",
)

METRIC = Metric(
    name="revenue", value=1000.0, unit="EUR",
    timestamp=datetime(2024, 1, 15), dimensions={},
)


class FakeIngestUseCase:
    def execute(self, filters: dict[str, Any], user_role: str) -> list[Transaction]:
        if user_role not in ("admin", "analyst"):
            raise PermissionError("Forbidden")
        return [TRANSACTION]


class FakeExportUseCase:
    def execute(self, filters: dict[str, Any], user_role: str) -> list[Metric]:
        if user_role not in ("admin", "analyst", "viewer"):
            raise PermissionError("Forbidden")
        return [METRIC]


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService(generator=FakeTokenGenerator(), verifier=FakeTokenVerifier())


@pytest.fixture
def client(auth_service: AuthService) -> TestClient:
    app = create_app(
        auth_service=auth_service,
        ingest_use_case=FakeIngestUseCase(),
        export_use_case=FakeExportUseCase(),
    )
    return TestClient(app)


def get_token(client: TestClient, user_id: str = "usr-001", role: str = "admin") -> str:
    response = client.post("/auth/token", json={"user_id": user_id, "role": role})
    return response.json()["access_token"]


class TestHealthEndpoint:
    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthEndpoint:
    def test_token_returns_access_token(self, client: TestClient) -> None:
        response = client.post("/auth/token", json={"user_id": "usr-001", "role": "admin"})
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_token_returns_bearer_type(self, client: TestClient) -> None:
        response = client.post("/auth/token", json={"user_id": "usr-001", "role": "admin"})
        assert response.json()["token_type"] == "bearer"


class TestTransactionsEndpoint:
    def test_ingest_requires_auth(self, client: TestClient) -> None:
        response = client.post("/api/transactions/ingest", json={})
        assert response.status_code == 401

    def test_ingest_succeeds_with_valid_token(self, client: TestClient) -> None:
        token = get_token(client, role="admin")
        response = client.post(
            "/api/transactions/ingest",
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestMetricsEndpoint:
    def test_export_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/metrics")
        assert response.status_code == 401

    def test_export_succeeds_with_valid_token(self, client: TestClient) -> None:
        token = get_token(client, role="viewer")
        response = client.get(
            "/api/metrics",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_export_returns_metric_fields(self, client: TestClient) -> None:
        token = get_token(client, role="admin")
        response = client.get(
            "/api/metrics",
            headers={"Authorization": f"Bearer {token}"},
        )
        metric = response.json()[0]
        assert metric["name"] == "revenue"
        assert metric["value"] == 1000.0
        assert metric["unit"] == "EUR"
