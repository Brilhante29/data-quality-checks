from __future__ import annotations

import csv
import hashlib
import json
import random
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from data_quality.domain import (
    CURRENCY_ALLOWED,
    CUSTOMER_REQUIRED,
    STATUS_ALLOWED,
    TOTAL_CONSISTENT,
    QUANTITY_RANGE,
    EXPECTED_COLUMNS,
)


@dataclass(frozen=True)
class Fixture:
    csv_path: Path
    truth_path: Path
    rows: int
    sha256: str
    truth: dict[int, tuple[str, ...]]


def generate_fixture(directory: Path, rows: int, seed: int = 42) -> Fixture:
    if rows < 20:
        raise ValueError("fixture requires at least 20 rows")
    directory.mkdir(parents=True, exist_ok=False)
    rng = random.Random(seed)
    csv_path = directory / "orders.csv"
    truth: dict[int, tuple[str, ...]] = {}

    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=EXPECTED_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for row_id in range(rows):
            quantity = 1 + row_id % 5
            unit_price = Decimal(str(round(10.0 + rng.random() * 90.0, 2)))
            total_amount = unit_price * quantity
            row = {
                "row_id": row_id,
                "order_id": f"ORD-{row_id:08d}",
                "customer_id": f"CUS-{row_id % 10000:05d}",
                "quantity": quantity,
                "unit_price": format(unit_price, ".2f"),
                "total_amount": format(total_amount, ".2f"),
                "currency": ("BRL", "USD", "EUR")[row_id % 3],
                "status": ("created", "paid", "shipped", "cancelled")[row_id % 4],
            }
            if row_id % 20 == 0:
                defect = (row_id // 20) % 5
                if defect == 0:
                    row["customer_id"] = "   "
                    reasons = (CUSTOMER_REQUIRED,)
                elif defect == 1:
                    row["quantity"] = -1
                    reasons = (QUANTITY_RANGE, TOTAL_CONSISTENT)
                elif defect == 2:
                    row["currency"] = "BTC"
                    reasons = (CURRENCY_ALLOWED,)
                elif defect == 3:
                    row["total_amount"] = format(total_amount + Decimal("7.00"), ".2f")
                    reasons = (TOTAL_CONSISTENT,)
                else:
                    row["status"] = "unknown"
                    reasons = (STATUS_ALLOWED,)
                truth[row_id] = reasons
            writer.writerow(row)

    payload = csv_path.read_bytes()
    sha256 = hashlib.sha256(payload).hexdigest()
    truth_path = directory / "truth.json"
    truth_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "rows": rows,
                "seed": seed,
                "csv_sha256": sha256,
                "invalid_rows": {
                    str(row_id): list(reasons)
                    for row_id, reasons in truth.items()
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return Fixture(
        csv_path=csv_path,
        truth_path=truth_path,
        rows=rows,
        sha256=sha256,
        truth=truth,
    )
