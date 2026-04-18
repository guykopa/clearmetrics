import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clearmetrics.adapters.inbound.fastapi_api import create_app
from clearmetrics.adapters.outbound.postgresql_models import Base
from clearmetrics.adapters.outbound.postgresql_transaction_source_adapter import (
    PostgreSQLTransactionSourceAdapter,
)
from clearmetrics.adapters.outbound.postgresql_transaction_storage_adapter import (
    PostgreSQLTransactionStorageAdapter,
)
from clearmetrics.adapters.outbound.postgresql_metric_source_adapter import (
    PostgreSQLMetricSourceAdapter,
)
from clearmetrics.adapters.outbound.jwt_token_generator_adapter import (
    JWTTokenGeneratorAdapter,
)
from clearmetrics.adapters.outbound.jwt_token_verifier_adapter import (
    JWTTokenVerifierAdapter,
)
from clearmetrics.domain.services.etl_service import ETLService
from clearmetrics.domain.services.auth_service import AuthService
from clearmetrics.domain.services.quality_service import QualityService
from clearmetrics.domain.rules.not_null_rule import NotNullRule
from clearmetrics.domain.rules.positive_amount_rule import PositiveAmountRule
from clearmetrics.domain.rules.valid_currency_rule import ValidCurrencyRule
from clearmetrics.domain.rules.no_duplicate_rule import NoDuplicateRule
from clearmetrics.application.ingest_data import IngestDataUseCase
from clearmetrics.application.export_metrics import ExportMetricsUseCase
from clearmetrics.application.validate_data import ValidateDataUseCase

DATABASE_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

session = Session(engine)

source = PostgreSQLTransactionSourceAdapter(session=session)
storage = PostgreSQLTransactionStorageAdapter(session=session)
etl_service = ETLService(source=source, storage=storage)
ingest_use_case = IngestDataUseCase(etl_service=etl_service)

metric_source = PostgreSQLMetricSourceAdapter(session=session)
export_use_case = ExportMetricsUseCase(source=metric_source)

generator = JWTTokenGeneratorAdapter(secret=JWT_SECRET, algorithm=JWT_ALGORITHM)
verifier = JWTTokenVerifierAdapter(secret=JWT_SECRET, algorithm=JWT_ALGORITHM)
auth_service = AuthService(generator=generator, verifier=verifier)

quality_service = QualityService(rules=[
    NotNullRule(fields=["id", "amount", "currency", "account_id", "timestamp"]),
    PositiveAmountRule(),
    ValidCurrencyRule(),
    NoDuplicateRule(id_field="id"),
])
validate_use_case = ValidateDataUseCase(quality_service=quality_service)

app = create_app(
    auth_service=auth_service,
    ingest_use_case=ingest_use_case,
    export_use_case=export_use_case,
    validate_use_case=validate_use_case,
)
