from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from data_quality.domain import (
    EXPECTED_COLUMNS,
    OrderRecord,
    QualityOutcome,
    RowRejection,
    evaluate_record,
)


class ReferenceQualityEngine:
    def validate(
        self,
        input_path: Path,
        accepted_path: Path,
        quarantine_path: Path,
    ) -> QualityOutcome:
        seen_row_ids: set[int] = set()
        rejections: list[RowRejection] = []
        reason_counts: Counter[str] = Counter()
        total_rows = 0
        accepted_rows = 0

        with (
            input_path.open("r", encoding="utf-8", newline="") as source,
            accepted_path.open("w", encoding="utf-8", newline="") as accepted_stream,
            quarantine_path.open(
                "w",
                encoding="utf-8",
                newline="",
            ) as quarantine_stream,
        ):
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
                raise ValueError("input columns or order do not match the contract")
            accepted_writer = csv.DictWriter(
                accepted_stream,
                fieldnames=EXPECTED_COLUMNS,
                lineterminator="\n",
            )
            quarantine_writer = csv.DictWriter(
                quarantine_stream,
                fieldnames=(*EXPECTED_COLUMNS, "_reasons"),
                lineterminator="\n",
            )
            accepted_writer.writeheader()
            quarantine_writer.writeheader()

            for row in reader:
                if None in row or any(row[name] is None for name in EXPECTED_COLUMNS):
                    raise ValueError("input row does not match the contract")
                record = OrderRecord.from_mapping(row)
                if record.row_id in seen_row_ids:
                    raise ValueError("row_id must be unique")
                seen_row_ids.add(record.row_id)
                total_rows += 1
                reasons = evaluate_record(record)
                if reasons:
                    rejection = RowRejection(record.row_id, reasons)
                    rejections.append(rejection)
                    reason_counts.update(reasons)
                    quarantine_writer.writerow({**row, "_reasons": ";".join(reasons)})
                else:
                    accepted_rows += 1
                    accepted_writer.writerow(row)

        return QualityOutcome(
            total_rows=total_rows,
            accepted_rows=accepted_rows,
            rejections=tuple(rejections),
            reason_counts=dict(reason_counts),
        )
