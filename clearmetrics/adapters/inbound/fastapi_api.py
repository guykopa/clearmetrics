from typing import Any
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

from clearmetrics.domain.services.auth_service import AuthService


security = HTTPBearer()


class TokenRequest(BaseModel):
    user_id: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_app(
    auth_service: AuthService,
    ingest_use_case: Any,
    export_use_case: Any,
    validate_use_case: Any = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="clearmetrics API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    Instrumentator().instrument(app).expose(app)

    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict[str, str]:
        try:
            return auth_service.verify_token(credentials.credentials)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/auth/token", response_model=TokenResponse)
    def get_token(request: TokenRequest) -> TokenResponse:
        token = auth_service.generate_token(
            user_id=request.user_id, role=request.role
        )
        return TokenResponse(access_token=token)

    @app.post("/api/transactions/ingest")
    def ingest_transactions(
        filters: dict[str, Any] = {},
        user: dict[str, str] = Depends(get_current_user),
    ) -> list[dict[str, Any]]:
        try:
            transactions = ingest_use_case.execute(
                filters=filters, user_role=user["role"]
            )
            return [
                {
                    "id": t.id,
                    "amount": t.amount,
                    "currency": t.currency,
                    "account_id": t.account_id,
                    "timestamp": t.timestamp.isoformat(),
                    "source": t.source,
                }
                for t in transactions
            ]
        except PermissionError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
            )

    @app.get("/api/metrics")
    def export_metrics(
        user: dict[str, str] = Depends(get_current_user),
    ) -> list[dict[str, Any]]:
        try:
            metrics = export_use_case.execute(filters={}, user_role=user["role"])
            return [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp.isoformat(),
                    "dimensions": m.dimensions,
                }
                for m in metrics
            ]
        except PermissionError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
            )

    @app.post("/api/transactions/validate")
    def validate_transactions(
        body: dict[str, Any],
        user: dict[str, str] = Depends(get_current_user),
    ) -> list[dict[str, Any]]:
        if validate_use_case is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Validation not configured",
            )
        try:
            results = validate_use_case.execute(
                records=body.get("records", []), user_role=user["role"]
            )
            return [
                {
                    "rule_name": r.rule_name,
                    "passed": r.passed,
                    "failed_count": r.failed_count,
                    "error_samples": r.error_samples,
                }
                for r in results
            ]
        except PermissionError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
            )

    return app
