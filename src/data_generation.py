"""
Module for generating the 70,000 synthetic experiment records.
Implements exact lognormal cart values, Bernoulli outcomes, financial calculations, and data consistency assertions.
"""

from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from scipy.special import expit

from src.config import (
    SEED_DATA_GENERATION,
    TOTAL_USERS,
    USERS_PER_GROUP,
    CART_MEDIAN,
    CART_LOG_SIGMA,
    CONTROL_MIN_BASKET,
    TREATMENT_MIN_BASKET,
    CONTROL_DISCOUNT_RATE,
    TREATMENT_DISCOUNT_RATE,
    BASE_DISCOUNT_SENSITIVITY,
    REFUND_PROBABILITY,
    COGS_RATE,
    FULFILLMENT_COST,
    PAYMENT_FEE_RATE,
    REVERSE_LOGISTICS_COST,
    BETA_LOG_CART
)
from src.calibration import calibrate_parameters, compute_base_scores


def generate_experiment_dataset(
    seed: int = SEED_DATA_GENERATION,
    calibrated_intercept: Optional[float] = None,
    calibrated_sensitivity: Optional[float] = None
) -> pd.DataFrame:
    """
    Generate the complete 70,000-user synthetic A/B testing dataset.
    """
    if calibrated_intercept is None or calibrated_sensitivity is None:
        calibrated_intercept, calibrated_sensitivity, _ = calibrate_parameters()

    data_rng = np.random.Generator(np.random.PCG64(seed))

    # 1. Cart values (Lognormal)
    cart_values = np.round(
        data_rng.lognormal(
            mean=np.log(CART_MEDIAN),
            sigma=CART_LOG_SIGMA,
            size=TOTAL_USERS
        ),
        2
    )

    # 2. Customer types (35% returning)
    is_returning = data_rng.random(TOTAL_USERS) < 0.35
    customer_type = np.where(is_returning, "returning", "new")

    # 3. Device types
    device_type = data_rng.choice(
        ["mobile", "desktop", "tablet"],
        size=TOTAL_USERS,
        p=[0.65, 0.28, 0.07]
    )

    # 4. Traffic sources
    traffic_source = data_rng.choice(
        ["paid", "organic", "email"],
        size=TOTAL_USERS,
        p=[0.50, 0.35, 0.15]
    )

    # 5. Assigned timestamps over 28-day window
    day_offsets = data_rng.integers(0, 28, size=TOTAL_USERS)
    second_offsets = data_rng.integers(0, 86400, size=TOTAL_USERS)
    assigned_at = (
        pd.Timestamp("2026-01-01")
        + pd.to_timedelta(day_offsets, unit="D")
        + pd.to_timedelta(second_offsets, unit="s")
    )

    # 6. Variant assignment (exact 50:50 allocation)
    variant = np.array(
        ["Control"] * USERS_PER_GROUP
        + ["Treatment"] * USERS_PER_GROUP
    )
    data_rng.shuffle(variant)

    # 7. Eligibility
    eligible_control = cart_values >= CONTROL_MIN_BASKET
    eligible_treatment = cart_values >= TREATMENT_MIN_BASKET
    eligible_for_offer = np.where(
        variant == "Control",
        eligible_control,
        eligible_treatment
    )

    # 8. Base score and potential probabilities
    base_score = compute_base_scores(
        cart_values,
        is_returning,
        device_type,
        traffic_source
    )
    eta_control = (
        calibrated_intercept
        + base_score
        + BASE_DISCOUNT_SENSITIVITY * eligible_control
    )
    eta_treatment = (
        calibrated_intercept
        + base_score
        + (BASE_DISCOUNT_SENSITIVITY + calibrated_sensitivity)
        * eligible_treatment
    )

    probability_control = expit(eta_control)
    probability_treatment = expit(eta_treatment)

    purchase_probability = np.where(
        variant == "Control",
        probability_control,
        probability_treatment
    )

    # 9. Realized purchase outcome (Bernoulli trial)
    purchase_flag = data_rng.binomial(n=1, p=purchase_probability)

    # 10. Discount and order values
    offer_discount_rate = np.where(
        variant == "Control",
        CONTROL_DISCOUNT_RATE,
        TREATMENT_DISCOUNT_RATE
    )
    offer_applied = (
        (purchase_flag == 1) & eligible_for_offer
    ).astype(int)

    pre_discount_order_value = np.where(
        purchase_flag == 1,
        cart_values,
        0.0
    )
    discount_amount = np.where(
        offer_applied == 1,
        np.round(pre_discount_order_value * offer_discount_rate, 2),
        0.0
    )
    net_checkout_order_value = np.round(
        pre_discount_order_value - discount_amount,
        2
    )

    # 11. Refund simulation (only purchasers can refund)
    purchaser_mask = purchase_flag == 1
    num_purchasers = int(purchaser_mask.sum())
    refund_flag = np.zeros(TOTAL_USERS, dtype=int)
    refund_outcomes = data_rng.binomial(
        n=1,
        p=REFUND_PROBABILITY,
        size=num_purchasers
    )
    refund_flag[purchaser_mask] = refund_outcomes

    # 12. Accounting & financial metrics
    estimated_cogs = np.round(pre_discount_order_value * COGS_RATE, 2)
    retained_revenue = np.where(
        refund_flag == 1,
        0.0,
        net_checkout_order_value
    )
    retained_cogs = np.where(
        refund_flag == 1,
        0.0,
        estimated_cogs
    )
    fulfillment_cost = np.where(
        purchase_flag == 1,
        FULFILLMENT_COST,
        0.0
    )
    payment_processing_fee = np.round(
        net_checkout_order_value * PAYMENT_FEE_RATE,
        2
    )
    reverse_logistics_cost = np.where(
        refund_flag == 1,
        REVERSE_LOGISTICS_COST,
        0.0
    )
    contribution_profit = np.round(
        retained_revenue
        - retained_cogs
        - fulfillment_cost
        - payment_processing_fee
        - reverse_logistics_cost,
        2
    )

    # 13. Basket value bands
    bins = [-np.inf, 999.0, 1499.0, 2500.0, np.inf]
    labels = [
        "Below ₹999",
        "₹999–₹1,498.99",
        "₹1,499–₹2,499.99",
        "₹2,500 and above"
    ]
    basket_value_band = pd.cut(
        cart_values,
        bins=bins,
        labels=labels,
        right=False
    ).astype(str)

    log_cart_value = np.log(cart_values / CART_MEDIAN)

    # Build DataFrame
    df = pd.DataFrame({
        "user_id": [f"U{i:06d}" for i in range(1, TOTAL_USERS + 1)],
        "experiment_id": "discount_offer_2026",
        "assigned_at": assigned_at,
        "variant": variant,
        "cart_value": cart_values,
        "customer_type": customer_type,
        "device_type": device_type,
        "traffic_source": traffic_source,
        "eligible_under_control": eligible_control,
        "eligible_under_treatment": eligible_treatment,
        "eligible_for_offer": eligible_for_offer,
        "purchase_probability_control": probability_control,
        "purchase_probability_treatment": probability_treatment,
        "purchase_probability": purchase_probability,
        "purchase_flag": purchase_flag,
        "offer_discount_rate": offer_discount_rate,
        "offer_applied": offer_applied,
        "pre_discount_order_value": pre_discount_order_value,
        "discount_amount": discount_amount,
        "net_checkout_order_value": net_checkout_order_value,
        "refund_flag": refund_flag,
        "estimated_cogs": estimated_cogs,
        "retained_revenue": retained_revenue,
        "retained_cogs": retained_cogs,
        "fulfillment_cost": fulfillment_cost,
        "payment_processing_fee": payment_processing_fee,
        "reverse_logistics_cost": reverse_logistics_cost,
        "contribution_profit": contribution_profit,
        "basket_value_band": basket_value_band,
        "log_cart_value": log_cart_value
    })

    # Validate essential accounting consistency rules
    assert len(df) == TOTAL_USERS
    assert df["user_id"].is_unique
    assert (df["refund_flag"] <= df["purchase_flag"]).all()
    assert (df["offer_applied"] <= df["purchase_flag"]).all()
    assert (df["offer_applied"] <= df["eligible_for_offer"].astype(int)).all()

    non_purchasers = df["purchase_flag"] == 0
    financial_cols = [
        "estimated_cogs",
        "retained_revenue",
        "retained_cogs",
        "fulfillment_cost",
        "payment_processing_fee",
        "reverse_logistics_cost",
        "contribution_profit"
    ]
    assert (df.loc[non_purchasers, financial_cols] == 0).all().all()

    refunded = df["refund_flag"] == 1
    assert (df.loc[refunded, "retained_revenue"] == 0).all()
    assert (df.loc[refunded, "retained_cogs"] == 0).all()
    assert (df.loc[refunded, "reverse_logistics_cost"] == REVERSE_LOGISTICS_COST).all()

    return df


def save_dataset(df: pd.DataFrame, output_path: str = "data/synthetic/discount_ab_test_users.csv") -> Path:
    """
    Save DataFrame to CSV ensuring parent directories exist.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
