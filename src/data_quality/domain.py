from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from types import MappingProxyType

EXPECTED_COLUMNS = (
    "row_id",
    "order_id",
    "customer_id",
    "quantity",
    "unit_price",
    "total_amount",
    "currency",
    "status",
)
ALLOWED_CURRENCIES = frozenset({"BRL", "USD", "EUR"})
ALLOWED_STATUSES = frozenset({"created", "paid", "shipped", "cancelled"})
CUSTOMER_REQUIRED = "customer_required"
QUANTITY_RANGE = "quantity_range"
UNIT_PRICE_RANGE = "unit_price_range"
CURRENCY_ALLOWED = "currency_allowed"
STATUS_ALLOWED = "status_allowed"
TOTAL_CONSISTENT = "total_consistent"
IDENTIFIERS_REQUIRED = "identifiers_required"
RULE_IDS = (
    IDENTIFIERS_REQUIRED,
    CUSTOMER_REQUIRED,
    QUANTITY_RANGE,
    UNIT_PRICE_RANGE,
    CURRENCY_ALLOWED,
    STATUS_ALLOWED,
    TOTAL_CONSISTENT,
)


@dataclass(frozen=True)
class OrderRecord:
    row_id: int
    order_id: str
    customer_id: str
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    currency: str
    status: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, str]) -> OrderRecord:
        if tuple(row) != EXPECTED_COLUMNS:
            raise ValueError("input columns or order do not match the contract")
        try:
            return cls(
                row_id=int(row["row_id"]),
                order_id=row["order_id"],
                customer_id=row["customer_id"],
                quantity=int(row["quantity"]),
                unit_price=Decimal(row["unit_price"]),
                total_amount=Decimal(row["total_amount"]),
                currency=row["currency"],
                status=row["status"],
            )
        except (ValueError, InvalidOperation) as error:
            raise ValueError("input row contains an invalid scalar type") from error


def evaluate_record(record: OrderRecord) -> tuple[str, ...]:
    failures: list[str] = []
    if record.row_id < 0 or not record.order_id.strip():
        failures.append(IDENTIFIERS_REQUIRED)
    if not record.customer_id.strip():
        failures.append(CUSTOMER_REQUIRED)
    if not 1 <= record.quantity <= 100:
        failures.append(QUANTITY_RANGE)
    if not Decimal("0.01") <= record.unit_price <= Decimal("100000.00"):
        failures.append(UNIT_PRICE_RANGE)
    if record.currency not in ALLOWED_CURRENCIES:
        failures.append(CURRENCY_ALLOWED)
    if record.status not in ALLOWED_STATUSES:
        failures.append(STATUS_ALLOWED)
    expected_total = record.unit_price * record.quantity
    if abs(record.total_amount - expected_total) > Decimal("0.01"):
        failures.append(TOTAL_CONSISTENT)
    return tuple(failures)


@dataclass(frozen=True)
class RowRejection:
    row_id: int
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.row_id < 0:
            raise ValueError("rejected row_id must be non-negative")
        if not self.reasons:
            raise ValueError("rejection must contain at least one reason")
        if len(set(self.reasons)) != len(self.reasons):
            raise ValueError("rejection reasons must be unique")
        unknown = set(self.reasons) - set(RULE_IDS)
        if unknown:
            raise ValueError(f"unknown rejection reasons: {sorted(unknown)}")


@dataclass(frozen=True)
class QualityOutcome:
    total_rows: int
    accepted_rows: int
    rejections: tuple[RowRejection, ...]
    reason_counts: Mapping[str, int]

    def __post_init__(self) -> None:
        if self.total_rows < 1:
            raise ValueError("total_rows must be positive")
        if self.accepted_rows + len(self.rejections) != self.total_rows:
            raise ValueError("accepted and rejected rows must partition the input")
        row_ids = [rejection.row_id for rejection in self.rejections]
        if len(set(row_ids)) != len(row_ids):
            raise ValueError("rejected row IDs must be unique")
        expected_counts = {
            rule_id: sum(rule_id in rejection.reasons for rejection in self.rejections)
            for rule_id in RULE_IDS
        }
        normalized = {key: value for key, value in expected_counts.items() if value}
        if dict(self.reason_counts) != normalized:
            raise ValueError("reason_counts do not match row rejections")
        object.__setattr__(
            self,
            "reason_counts",
            MappingProxyType(dict(self.reason_counts)),
        )


@dataclass(frozen=True)
class DetectionMetrics:
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    precision: float
    recall: float
    f1: float
    rejected_rows_percent: float
    reason_exact_match_rate: float


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def score_outcome(
    total_rows: int,
    truth: Mapping[int, tuple[str, ...]],
    outcome: QualityOutcome,
) -> DetectionMetrics:
    if total_rows != outcome.total_rows:
        raise ValueError("truth and outcome row counts differ")
    if any(row_id < 0 or row_id >= total_rows for row_id in truth):
        raise ValueError("truth contains row ID outside the dataset")
    predicted = {
        rejection.row_id: rejection.reasons for rejection in outcome.rejections
    }
    truth_ids = set(truth)
    predicted_ids = set(predicted)
    true_positive = len(truth_ids & predicted_ids)
    false_positive = len(predicted_ids - truth_ids)
    false_negative = len(truth_ids - predicted_ids)
    true_negative = total_rows - true_positive - false_positive - false_negative
    precision = _ratio(true_positive, true_positive + false_positive)
    recall = _ratio(true_positive, true_positive + false_negative)
    f1 = _ratio(2 * precision * recall, precision + recall)
    exact = sum(predicted.get(row_id) == reasons for row_id, reasons in truth.items())
    return DetectionMetrics(
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
        precision=precision,
        recall=recall,
        f1=f1,
        rejected_rows_percent=100.0 * len(predicted_ids) / total_rows,
        reason_exact_match_rate=_ratio(exact, len(truth)),
    )
