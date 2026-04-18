from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from clearmetrics.ports.outbound.i_transaction_source_port import ITransactionSourcePort


class CSVTransactionSourceAdapter(ITransactionSourcePort):
    """Fetches transaction records from a CSV file using pandas."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def fetch_transactions(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Read the CSV file and return records matching the given filters."""
        if not self._file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self._file_path}")

        df = pd.read_csv(self._file_path, parse_dates=["timestamp"])

        for key, value in filters.items():
            if key in df.columns:
                df = df[df[key] == value]

        records = df.to_dict(orient="records")
        return [
            {**record, "timestamp": record["timestamp"].to_pydatetime()}
            for record in records
        ]
