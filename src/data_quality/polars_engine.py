from __future__ import annotations

from collections import Counter
from pathlib import Path

import polars as pl

from data_quality.domain import (
    ALLOWED_CURRENCIES,
    ALLOWED_STATUSES,
    CURRENCY_ALLOWED,
    CUSTOMER_REQUIRED,
    EXPECTED_COLUMNS,
    IDENTIFIERS_REQUIRED,
    QUANTITY_RANGE,
    STATUS_ALLOWED,
    TOTAL_CONSISTENT,
    UNIT_PRICE_RANGE,
    QualityOutcome,
    RowRejection,
)
from data_quality.schema import OrderInputSchema


class PolarsPanderaQualityEngine:
    def _read(self, input_path: Path) -> pl.DataFrame:
        frame = pl.read_csv(
            input_path,
            schema_overrides={
                "row_id": pl.Int64,
                "order_id": pl.String,
                "customer_id": pl.String,
                "quantity": pl.Int64,
                "unit_price": pl.Float64,
                "total_amount": pl.Float64,
                "currency": pl.String,
                "status": pl.String,
            },
        )
        if tuple(frame.columns) != EXPECTED_COLUMNS:
            raise ValueError("input columns or order do not match the contract")
        validated = OrderInputSchema.validate(frame, lazy=True)
        if validated["row_id"].n_unique() != validated.height:
            raise ValueError("row_id must be unique")
        return validated

    def validate(
        self,
        input_path: Path,
        accepted_path: Path,
        quarantine_path: Path,
    ) -> QualityOutcome:
        frame = self._read(input_path)
        rules = (
            (
                IDENTIFIERS_REQUIRED,
                (pl.col("row_id") < 0)
                | (pl.col("order_id").str.strip_chars().str.len_chars() == 0),
            ),
            (
                CUSTOMER_REQUIRED,
                pl.col("customer_id").str.strip_chars().str.len_chars() == 0,
            ),
            (
                QUANTITY_RANGE,
                (pl.col("quantity") < 1) | (pl.col("quantity") > 100),
            ),
            (
                UNIT_PRICE_RANGE,
                (pl.col("unit_price") < 0.01)
                | (pl.col("unit_price") > 100000.0),
            ),
            (
                CURRENCY_ALLOWED,
                ~pl.col("currency").is_in(sorted(ALLOWED_CURRENCIES)),
            ),
            (
                STATUS_ALLOWED,
                ~pl.col("status").is_in(sorted(ALLOWED_STATUSES)),
            ),
            (
                TOTAL_CONSISTENT,
                (
                    pl.col("total_amount")
                    - pl.col("unit_price") * pl.col("quantity")
                ).abs()
                > 0.01,
            ),
        )
        flag_names = [f"_fail_{rule_id}" for rule_id, _ in rules]
        evaluated = frame.with_columns(
            expression.fill_null(True).alias(flag_name)
            for flag_name, (_, expression) in zip(flag_names, rules, strict=True)
        ).with_columns(
            pl.any_horizontal(*(pl.col(name) for name in flag_names)).alias(
                "_rejected"
            )
        )

        accepted = evaluated.filter(~pl.col("_rejected")).drop(
            *flag_names,
            "_rejected",
        )
        rejected_with_flags = evaluated.filter(pl.col("_rejected"))
        rejections: list[RowRejection] = []
        reason_counts: Counter[str] = Counter()
        reasons_text: list[str] = []
        rule_ids = [rule_id for rule_id, _ in rules]
        for row in rejected_with_flags.select("row_id", *flag_names).iter_rows(
            named=True
        ):
            reasons = tuple(
                rule_id
                for rule_id, flag_name in zip(rule_ids, flag_names, strict=True)
                if row[flag_name]
            )
            rejection = RowRejection(row_id=int(row["row_id"]), reasons=reasons)
            rejections.append(rejection)
            reason_counts.update(reasons)
            reasons_text.append(";".join(reasons))

        rejected = rejected_with_flags.drop(*flag_names, "_rejected").with_columns(
            pl.Series("_reasons", reasons_text, dtype=pl.String)
        )
        accepted.write_csv(accepted_path)
        rejected.write_csv(quarantine_path)
        return QualityOutcome(
            total_rows=frame.height,
            accepted_rows=accepted.height,
            rejections=tuple(rejections),
            reason_counts=dict(reason_counts),
        )
