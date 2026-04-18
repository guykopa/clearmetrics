import json
import pytest
from datetime import datetime
import httpx

from clearmetrics.adapters.outbound.external_api_transaction_source_adapter import (
    ExternalAPITransactionSourceAdapter,
)
from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort

API_RECORDS = [
    {
        "id": "txn-001",
        "amount": 150.75,
        "currency": "EUR",
        "account_id": "acc-001",
        "timestamp": "2024-01-15T10:30:00",
        "source": "external_api",
    },
    {
        "id": "txn-002",
        "amount": 200.00,
        "currency": "USD",
        "account_id": "acc-002",
        "timestamp": "2024-01-16T09:00:00",
        "source": "external_api",
    },
]


def make_mock_client(records: list[dict], status_code: int = 200) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=status_code, json=records)

    return httpx.Client(transport=httpx.MockTransport(handler))


class TestExternalAPITransactionSourceAdapter:
    def test_implements_port(self) -> None:
        client = make_mock_client(API_RECORDS)
        adapter = ExternalAPITransactionSourceAdapter(
            client=client, base_url="http://api.example.com"
        )
        assert isinstance(adapter, ITransactionSourcePort)

    def test_fetch_returns_all_records(self) -> None:
        client = make_mock_client(API_RECORDS)
        adapter = ExternalAPITransactionSourceAdapter(
            client=client, base_url="http://api.example.com"
        )
        result = adapter.fetch_transactions(filters={})
        assert len(result) == 2

    def test_fetch_returns_correct_fields(self) -> None:
        client = make_mock_client(API_RECORDS)
        adapter = ExternalAPITransactionSourceAdapter(
            client=client, base_url="http://api.example.com"
        )
        record = adapter.fetch_transactions(filters={})[0]
        assert record["id"] == "txn-001"
        assert record["amount"] == 150.75
        assert record["currency"] == "EUR"
        assert record["source"] == "external_api"

    def test_fetch_timestamp_is_datetime(self) -> None:
        client = make_mock_client(API_RECORDS)
        adapter = ExternalAPITransactionSourceAdapter(
            client=client, base_url="http://api.example.com"
        )
        record = adapter.fetch_transactions(filters={})[0]
        assert isinstance(record["timestamp"], datetime)

    def test_fetch_passes_filters_as_params(self) -> None:
        received_params: list[dict] = []

        def handler(request: httpx.Request) -> httpx.Response:
            received_params.append(dict(request.url.params))
            return httpx.Response(200, json=[])

        client = httpx.Client(transport=httpx.MockTransport(handler))
        adapter = ExternalAPITransactionSourceAdapter(
            client=client, base_url="http://api.example.com"
        )
        adapter.fetch_transactions(filters={"account_id": "acc-001"})
        assert received_params[0]["account_id"] == "acc-001"

    def test_raises_on_http_error(self) -> None:
        client = make_mock_client([], status_code=500)
        adapter = ExternalAPITransactionSourceAdapter(
            client=client, base_url="http://api.example.com"
        )
        with pytest.raises(httpx.HTTPStatusError):
            adapter.fetch_transactions(filters={})

    def test_fetch_returns_empty_on_empty_response(self) -> None:
        client = make_mock_client([])
        adapter = ExternalAPITransactionSourceAdapter(
            client=client, base_url="http://api.example.com"
        )
        result = adapter.fetch_transactions(filters={})
        assert result == []
