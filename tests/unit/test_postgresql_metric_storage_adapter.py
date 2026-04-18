import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clearmetrics.adapters.outbound.postgresql_models import Base
from clearmetrics.adapters.outbound.postgresql_metric_source_adapter import PostgreSQLMetricSourceAdapter
from clearmetrics.ports.outbound.i_metric_storage_port import IMetricStoragePort

RAW = {
    "name": "total_revenue",
    "value": 9171.5,
    "unit": "EUR",
    "timestamp": datetime(2024, 1, 19, 17, 0),
    "dimensions": {"period": "2024-01"},
}


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


class TestPostgreSQLMetricStorageAdapter:
    def test_implements_port(self, session: Session) -> None:
        from clearmetrics.adapters.outbound.postgresql_metric_storage_adapter import PostgreSQLMetricStorageAdapter
        adapter = PostgreSQLMetricStorageAdapter(session=session)
        assert isinstance(adapter, IMetricStoragePort)

    def test_save_persists_metric(self, session: Session) -> None:
        from clearmetrics.adapters.outbound.postgresql_metric_storage_adapter import PostgreSQLMetricStorageAdapter
        storage = PostgreSQLMetricStorageAdapter(session=session)
        storage.save_metric(RAW)
        session.commit()

        source = PostgreSQLMetricSourceAdapter(session=session)
        result = source.fetch_metrics(filters={})
        assert len(result) == 1

    def test_save_stores_all_fields(self, session: Session) -> None:
        from clearmetrics.adapters.outbound.postgresql_metric_storage_adapter import PostgreSQLMetricStorageAdapter
        storage = PostgreSQLMetricStorageAdapter(session=session)
        storage.save_metric(RAW)
        session.commit()

        source = PostgreSQLMetricSourceAdapter(session=session)
        record = source.fetch_metrics(filters={})[0]
        assert record["name"] == RAW["name"]
        assert record["value"] == RAW["value"]
        assert record["unit"] == RAW["unit"]
        assert record["dimensions"] == RAW["dimensions"]

    def test_save_multiple_metrics(self, session: Session) -> None:
        from clearmetrics.adapters.outbound.postgresql_metric_storage_adapter import PostgreSQLMetricStorageAdapter
        storage = PostgreSQLMetricStorageAdapter(session=session)
        storage.save_metric(RAW)
        storage.save_metric({**RAW, "name": "avg_amount", "value": 1834.3})
        session.commit()

        source = PostgreSQLMetricSourceAdapter(session=session)
        result = source.fetch_metrics(filters={})
        assert len(result) == 2
