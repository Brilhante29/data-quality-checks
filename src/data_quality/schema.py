from __future__ import annotations

import pandera.polars as pa


class OrderInputSchema(pa.DataFrameModel):
    row_id: int
    order_id: str
    customer_id: str
    quantity: int
    unit_price: float
    total_amount: float
    currency: str
    status: str

    class Config:
        strict = True
        coerce = False
