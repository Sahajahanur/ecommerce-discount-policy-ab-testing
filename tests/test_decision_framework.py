"""
Unit tests for the pre-registered A/B/C decision framework, verifying Outcome C precedence and adoption rules.
"""

from src.decision_framework import evaluate_decision_framework


def test_outcome_c_precedence_profit_harm():
    """Verify Outcome C is triggered if profit CI upper bound is below 0, regardless of conversion lift."""
    decision = evaluate_decision_framework(
        p_value=0.000001,
        absolute_conversion_lift=0.03,  # Massive 3 pp lift
        profit_ci_lower=-5.0,
        profit_ci_upper=-0.5,           # Upper bound strictly negative
        refund_ci_lower=-0.01,
        refund_ci_upper=0.01
    )
    assert decision["final_decision"] == "C"
    assert decision["recommendation"] == "Reject Treatment"
    assert decision["rejection_conditions"]["reject_profit"] is True


def test_outcome_c_precedence_refund_spike():
    """Verify Outcome C is triggered if refund CI lower bound exceeds 0.03, regardless of profit or conversion."""
    decision = evaluate_decision_framework(
        p_value=0.00001,
        absolute_conversion_lift=0.02,
        profit_ci_lower=2.0,
        profit_ci_upper=8.0,
        refund_ci_lower=0.035,          # Lower bound > 0.03
        refund_ci_upper=0.060
    )
    assert decision["final_decision"] == "C"
    assert decision["recommendation"] == "Reject Treatment"
    assert decision["rejection_conditions"]["reject_refund"] is True


def test_outcome_a_all_criteria_met():
    """Verify Outcome A is triggered when all 4 adoption criteria are met and no rejection applies."""
    decision = evaluate_decision_framework(
        p_value=9.28e-8,
        absolute_conversion_lift=0.009257,
        profit_ci_lower=0.0329,
        profit_ci_upper=3.7717,
        refund_ci_lower=-0.020084,
        refund_ci_upper=0.014427
    )
    assert decision["final_decision"] == "A"
    assert decision["recommendation"] == "Adopt Treatment"
    assert all(decision["adoption_conditions"].values())


def test_outcome_b_insufficient_practical_lift():
    """Verify Outcome B triggers if lift is statistically significant but below practical threshold (0.005)."""
    decision = evaluate_decision_framework(
        p_value=0.01,
        absolute_conversion_lift=0.003,  # Less than 0.005 threshold
        profit_ci_lower=0.5,
        profit_ci_upper=2.0,
        refund_ci_lower=-0.01,
        refund_ci_upper=0.01
    )
    assert decision["final_decision"] == "B"
    assert decision["recommendation"] == "Retain Control / Inconclusive"
    assert decision["adoption_conditions"]["practical_conversion_lift"] is False


def test_outcome_b_neutral_profit():
    """Verify Outcome B triggers if profit lower confidence bound fails to clear strictly above 0."""
    decision = evaluate_decision_framework(
        p_value=0.001,
        absolute_conversion_lift=0.01,
        profit_ci_lower=-0.05,          # Lower bound <= 0
        profit_ci_upper=3.0,
        refund_ci_lower=-0.01,
        refund_ci_upper=0.01
    )
    assert decision["final_decision"] == "B"
    assert decision["recommendation"] == "Retain Control / Inconclusive"
    assert decision["adoption_conditions"]["positive_profit_evidence"] is False


def test_outcome_b_statistically_non_significant():
    """Verify Outcome B triggers if conversion p-value >= 0.05."""
    decision = evaluate_decision_framework(
        p_value=0.12,                   # Insufficient statistical significance
        absolute_conversion_lift=0.006,
        profit_ci_lower=0.5,
        profit_ci_upper=3.0,
        refund_ci_lower=-0.01,
        refund_ci_upper=0.01
    )
    assert decision["final_decision"] == "B"
    assert decision["recommendation"] == "Retain Control / Inconclusive"
    assert decision["adoption_conditions"]["statistical_significance"] is False
