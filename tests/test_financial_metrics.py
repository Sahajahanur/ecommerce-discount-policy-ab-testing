"""
Unit tests for financial accounting, bootstrap confidence intervals, and refund guardrail calculations.
"""

import pytest
import numpy as np
import pandas as pd
from src.financial_metrics import (
    compute_financial_summary,
    bootstrap_mean_difference,
    calculate_refund_guardrail_ci
)


@pytest.fixture
def sample_financial_df():
    """Create a minimal synthetic dataframe satisfying accounting consistency rules."""
    records = []
    # Control user 1: non-purchaser
    records.append({
        "user_id": "U001", "variant": "Control", "purchase_flag": 0, "refund_flag": 0,
        "pre_discount_order_value": 0.0, "net_checkout_order_value": 0.0,
        "retained_revenue": 0.0, "estimated_cogs": 0.0, "retained_cogs": 0.0,
        "fulfillment_cost": 0.0, "payment_processing_fee": 0.0, "reverse_logistics_cost": 0.0,
        "contribution_profit": 0.0
    })
    # Control user 2: purchaser, no refund (cart 1200, 10% off -> net 1080)
    # COGS = 720, fulfillment = 60, fee = 21.60, profit = 1080 - 720 - 60 - 21.60 = 278.40
    records.append({
        "user_id": "U002", "variant": "Control", "purchase_flag": 1, "refund_flag": 0,
        "pre_discount_order_value": 1200.0, "net_checkout_order_value": 1080.0,
        "retained_revenue": 1080.0, "estimated_cogs": 720.0, "retained_cogs": 720.0,
        "fulfillment_cost": 60.0, "payment_processing_fee": 21.60, "reverse_logistics_cost": 0.0,
        "contribution_profit": 278.40
    })
    # Control user 3: purchaser, refunded
    # retained_rev = 0, retained_cogs = 0, fulfillment = 60, fee = 21.60, rev_log = 80, profit = -161.60
    records.append({
        "user_id": "U003", "variant": "Control", "purchase_flag": 1, "refund_flag": 1,
        "pre_discount_order_value": 1200.0, "net_checkout_order_value": 1080.0,
        "retained_revenue": 0.0, "estimated_cogs": 720.0, "retained_cogs": 0.0,
        "fulfillment_cost": 60.0, "payment_processing_fee": 21.60, "reverse_logistics_cost": 80.0,
        "contribution_profit": -161.60
    })
    # Treatment user 4: purchaser, no refund (cart 2000, 15% off -> net 1700)
    # COGS = 1200, fulfillment = 60, fee = 34.0, profit = 1700 - 1200 - 60 - 34 = 406.00
    records.append({
        "user_id": "U004", "variant": "Treatment", "purchase_flag": 1, "refund_flag": 0,
        "pre_discount_order_value": 2000.0, "net_checkout_order_value": 1700.0,
        "retained_revenue": 1700.0, "estimated_cogs": 1200.0, "retained_cogs": 1200.0,
        "fulfillment_cost": 60.0, "payment_processing_fee": 34.0, "reverse_logistics_cost": 0.0,
        "contribution_profit": 406.00
    })
    return pd.DataFrame(records)


def test_financial_summary_accounting(sample_financial_df):
    """Verify financial aggregation logic and formulas."""
    summary = compute_financial_summary(sample_financial_df)
    ctrl = summary["control"]
    trt = summary["treatment"]

    assert ctrl["total_users"] == 3
    assert ctrl["purchasers"] == 2
    assert ctrl["refunds"] == 1
    assert ctrl["retained_revenue_total"] == 1080.0
    assert pytest.approx(ctrl["contribution_profit_total"], abs=1e-2) == 116.80
    assert pytest.approx(ctrl["purchaser_refund_rate"], abs=1e-3) == 0.50

    assert trt["total_users"] == 1
    assert trt["purchasers"] == 1
    assert trt["refunds"] == 0
    assert trt["retained_revenue_total"] == 1700.0
    assert trt["contribution_profit_total"] == 406.00
    assert trt["purchaser_refund_rate"] == 0.0


def test_bootstrap_mean_difference_reproducibility():
    """Verify bootstrap function executes reproducibly with fixed random seed."""
    rng1 = np.random.default_rng(2027)
    rng2 = np.random.default_rng(2027)

    c = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    t = np.array([15.0, 25.0, 35.0, 45.0, 60.0])

    diff1, low1, high1 = bootstrap_mean_difference(c, t, rng1, repetitions=500)
    diff2, low2, high2 = bootstrap_mean_difference(c, t, rng2, repetitions=500)

    assert diff1 == diff2
    assert low1 == low2
    assert high1 == high2
    assert low1 < high1
    assert low1 <= diff1 <= high1


def test_refund_guardrail_ci():
    """Verify refund rate Newcombe confidence interval logic on verified counts."""
    # Verified counts: Control: 147 / 1787; Treatment: 168 / 2111
    df_mock = pd.DataFrame({
        "variant": ["Treatment"] * 2111 + ["Control"] * 1787,
        "purchase_flag": [1] * (2111 + 1787),
        "refund_flag": [1] * 168 + [0] * (2111 - 168) + [1] * 147 + [0] * (1787 - 147)
    })

    res = calculate_refund_guardrail_ci(df_mock)
    assert pytest.approx(res["difference"] * 100, abs=1e-2) == -0.2678
    assert pytest.approx(res["lower_bound"] * 100, abs=1e-2) == -2.0084
    assert pytest.approx(res["upper_bound"] * 100, abs=1e-2) == 1.4427
    assert res["guardrail_satisfied"] is True
    assert res["rejection_triggered"] is False
