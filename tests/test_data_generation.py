"""
Unit tests for data generation logic, column completeness, and financial consistency assertions.
"""

import pytest
import numpy as np
import pandas as pd
from src.data_generation import generate_experiment_dataset
from src.config import (
    TOTAL_USERS,
    USERS_PER_GROUP,
    REVERSE_LOGISTICS_COST
)


@pytest.fixture(scope="module")
def experiment_df():
    """Generate or load experiment dataset once for module-level tests."""
    return generate_experiment_dataset()


def test_dataset_dimensions_and_splits(experiment_df):
    """Verify dataset dimensions and 50:50 allocation."""
    assert len(experiment_df) == TOTAL_USERS
    assert experiment_df.shape[1] == 30
    assert experiment_df["user_id"].nunique() == TOTAL_USERS

    val_counts = experiment_df["variant"].value_counts()
    assert val_counts["Control"] == USERS_PER_GROUP
    assert val_counts["Treatment"] == USERS_PER_GROUP


def test_no_null_values(experiment_df):
    """Verify absence of missing or NaN values across all columns."""
    assert experiment_df.isnull().sum().sum() == 0


def test_purchase_and_offer_flags(experiment_df):
    """Verify logical relationship between purchases, eligibility, and applied offers."""
    # Only purchasers can have offer applied
    assert (experiment_df["offer_applied"] <= experiment_df["purchase_flag"]).all()
    # Offer can only be applied if eligible
    assert (experiment_df["offer_applied"] <= experiment_df["eligible_for_offer"].astype(int)).all()
    # Discounts are only positive if offer applied
    assert (experiment_df.loc[experiment_df["offer_applied"] == 0, "discount_amount"] == 0.0).all()


def test_refund_logic(experiment_df):
    """Verify refunds only occur among purchasers."""
    assert (experiment_df["refund_flag"] <= experiment_df["purchase_flag"]).all()
    non_purchasers = experiment_df["purchase_flag"] == 0
    assert (experiment_df.loc[non_purchasers, "refund_flag"] == 0).all()


def test_financial_accounting_consistency(experiment_df):
    """Verify strict financial rules for non-purchasers and refunded orders."""
    non_purchasers = experiment_df["purchase_flag"] == 0
    financial_cols = [
        "estimated_cogs",
        "retained_revenue",
        "retained_cogs",
        "fulfillment_cost",
        "payment_processing_fee",
        "reverse_logistics_cost",
        "contribution_profit"
    ]
    assert (experiment_df.loc[non_purchasers, financial_cols] == 0.0).all().all()

    refunded = experiment_df["refund_flag"] == 1
    assert (experiment_df.loc[refunded, "retained_revenue"] == 0.0).all()
    assert (experiment_df.loc[refunded, "retained_cogs"] == 0.0).all()
    assert (experiment_df.loc[refunded, "reverse_logistics_cost"] == REVERSE_LOGISTICS_COST).all()
