from decimal import Decimal

import pytest

from data_quality.domain import (
    CURRENCY_ALLOWED,
    CUSTOMER_REQUIRED,
    IDENTIFIERS_REQUIRED,
    QUANTITY_RANGE,
    STATUS_ALLOWED,
    TOTAL_CONSISTENT,
    UNIT_PRICE_RANGE,
    OrderRecord,
    QualityOutcome,
    RowRejection,
    evaluate_record,
    score_outcome,
)


def valid_record(**changes):
    values = {
        "row_id": 1,
        "order_id": "ORD-1",
        "customer_id": "CUS-1",
        "quantity": 2,
        "unit_price": Decimal("10.00"),
        "total_amount": Decimal("20.00"),
        "currency": "BRL",
        "status": "paid",
    }
    values.update(changes)
    return OrderRecord(**values)


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"row_id": -1}, IDENTIFIERS_REQUIRED),
        ({"order_id": " "}, IDENTIFIERS_REQUIRED),
        ({"customer_id": "  "}, CUSTOMER_REQUIRED),
        ({"quantity": 0}, QUANTITY_RANGE),
        ({"unit_price": Decimal("0.00")}, UNIT_PRICE_RANGE),
        ({"currency": "BTC"}, CURRENCY_ALLOWED),
        ({"status": "unknown"}, STATUS_ALLOWED),
        ({"total_amount": Decimal("21.00")}, TOTAL_CONSISTENT),
    ],
)
def test_rule_policy_reports_each_failure(changes, reason):
    assert reason in evaluate_record(valid_record(**changes))


def test_rule_policy_accepts_valid_order_and_combines_reasons():
    assert evaluate_record(valid_record()) == ()
    reasons = evaluate_record(
        valid_record(customer_id="", currency="BTC", status="unknown")
    )
    assert reasons == (CUSTOMER_REQUIRED, CURRENCY_ALLOWED, STATUS_ALLOWED)


def test_record_parser_rejects_schema_or_scalar_type():
    row = {
        "row_id": "1",
        "order_id": "ORD-1",
        "customer_id": "CUS-1",
        "quantity": "2",
        "unit_price": "10.00",
        "total_amount": "20.00",
        "currency": "BRL",
        "status": "paid",
    }
    assert OrderRecord.from_mapping(row).quantity == 2
    bad_order = {
        "order_id": row["order_id"],
        **{key: value for key, value in row.items() if key != "order_id"},
    }
    with pytest.raises(ValueError, match="columns or order"):
        OrderRecord.from_mapping(bad_order)
    row["quantity"] = "not-int"
    with pytest.raises(ValueError, match="scalar type"):
        OrderRecord.from_mapping(row)


def test_outcome_scoring_measures_rows_and_exact_reason():
    truth = {0: (CUSTOMER_REQUIRED,), 2: (CURRENCY_ALLOWED,)}
    outcome = QualityOutcome(
        total_rows=4,
        accepted_rows=1,
        rejections=(
            RowRejection(0, (CUSTOMER_REQUIRED,)),
            RowRejection(1, (STATUS_ALLOWED,)),
            RowRejection(2, (CURRENCY_ALLOWED,)),
        ),
        reason_counts={
            CUSTOMER_REQUIRED: 1,
            STATUS_ALLOWED: 1,
            CURRENCY_ALLOWED: 1,
        },
    )

    metrics = score_outcome(4, truth, outcome)

    assert metrics.true_positive == 2
    assert metrics.false_positive == 1
    assert metrics.true_negative == 1
    assert metrics.false_negative == 0
    assert metrics.precision == pytest.approx(2 / 3)
    assert metrics.recall == 1.0
    assert metrics.reason_exact_match_rate == 1.0
    assert metrics.rejected_rows_percent == 75.0


def test_domain_rejects_inconsistent_outcome_and_truth():
    with pytest.raises(ValueError, match="partition"):
        QualityOutcome(2, 2, (RowRejection(1, (STATUS_ALLOWED,)),), {STATUS_ALLOWED: 1})
    with pytest.raises(ValueError, match="reason_counts"):
        QualityOutcome(2, 1, (RowRejection(1, (STATUS_ALLOWED,)),), {})
    outcome = QualityOutcome(
        2,
        1,
        (RowRejection(1, (STATUS_ALLOWED,)),),
        {STATUS_ALLOWED: 1},
    )
    with pytest.raises(ValueError, match="row counts"):
        score_outcome(3, {}, outcome)
    with pytest.raises(ValueError, match="outside"):
        score_outcome(2, {3: (STATUS_ALLOWED,)}, outcome)


def test_row_rejection_rejects_empty_duplicate_or_unknown_reason():
    with pytest.raises(ValueError):
        RowRejection(1, ())
    with pytest.raises(ValueError):
        RowRejection(1, (STATUS_ALLOWED, STATUS_ALLOWED))
    with pytest.raises(ValueError):
        RowRejection(1, ("unknown",))
