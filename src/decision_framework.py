"""
Module implementing the pre-registered A/B/C business decision rules with strict Outcome C precedence.
"""

from typing import Dict, Any

from src.config import (
    ALPHA,
    PRACTICAL_CONVERSION_THRESHOLD,
    MIN_ACCEPTABLE_PROFIT_DIFF,
    REFUND_GUARDRAIL
)


def evaluate_decision_framework(
    p_value: float,
    absolute_conversion_lift: float,
    profit_ci_lower: float,
    profit_ci_upper: float,
    refund_ci_lower: float,
    refund_ci_upper: float,
    alpha: float = ALPHA,
    practical_threshold: float = PRACTICAL_CONVERSION_THRESHOLD,
    profit_floor: float = MIN_ACCEPTABLE_PROFIT_DIFF,
    refund_limit: float = REFUND_GUARDRAIL
) -> Dict[str, Any]:
    """
    Evaluate precedence-ordered business decision framework:
    1. Outcome C takes strict precedence: Reject if profit CI upper bound < 0 OR refund diff CI lower bound > 0.03.
    2. Outcome A applies only if C does not trigger AND all 4 criteria pass:
       p_value < alpha, lift >= practical_threshold, profit CI lower > 0, refund CI upper <= 0.03.
    3. Outcome B applies otherwise (Retain Control / Inconclusive).
    """
    # 1. Evaluate rejection conditions (Outcome C)
    reject_profit = profit_ci_upper < profit_floor
    reject_refund = refund_ci_lower > refund_limit

    # 2. Evaluate adoption conditions (Outcome A)
    adoption_conditions = {
        "statistical_significance": bool(p_value < alpha),
        "practical_conversion_lift": bool(absolute_conversion_lift >= practical_threshold),
        "positive_profit_evidence": bool(profit_ci_lower > profit_floor),
        "refund_guardrail_satisfied": bool(refund_ci_upper <= refund_limit)
    }

    # 3. Apply hierarchy
    if reject_profit or reject_refund:
        final_decision = "C"
        recommendation = "Reject Treatment"
        rationale = "Rejection guardrail triggered (economic harm or refund rate spike)."
    elif all(adoption_conditions.values()):
        final_decision = "A"
        recommendation = "Adopt Treatment"
        rationale = "Statistically significant, practically meaningful, economically positive, and guarded against refunds."
    else:
        final_decision = "B"
        recommendation = "Retain Control / Inconclusive"
        rationale = "Failed to clear all adoption criteria without triggering rejection."

    return {
        "final_decision": final_decision,
        "recommendation": recommendation,
        "rationale": rationale,
        "rejection_conditions": {
            "reject_profit": bool(reject_profit),
            "reject_refund": bool(reject_refund)
        },
        "adoption_conditions": adoption_conditions,
        "inputs": {
            "p_value": float(p_value),
            "absolute_conversion_lift": float(absolute_conversion_lift),
            "profit_ci_lower": float(profit_ci_lower),
            "profit_ci_upper": float(profit_ci_upper),
            "refund_ci_lower": float(refund_ci_lower),
            "refund_ci_upper": float(refund_ci_upper)
        }
    }
