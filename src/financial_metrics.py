"""
Module for computing financial metrics, AOV, profitability, refund rates, and bootstrap confidence intervals.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from statsmodels.stats.proportion import confint_proportions_2indep

from src.config import (
    SEED_BOOTSTRAP,
    BOOTSTRAP_REPETITIONS,
    REFUND_GUARDRAIL
)


def compute_financial_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute point estimates for monetary metrics and refund rates by variant.
    """
    ctrl = df[df["variant"] == "Control"]
    trt = df[df["variant"] == "Treatment"]

    def group_stats(group_df: pd.DataFrame):
        n_users = len(group_df)
        purchasers = group_df[group_df["purchase_flag"] == 1]
        n_purchasers = len(purchasers)
        n_refunds = int(purchasers["refund_flag"].sum())

        retained_rev_total = float(group_df["retained_revenue"].sum())
        profit_total = float(group_df["contribution_profit"].sum())

        gross_aov = float(purchasers["pre_discount_order_value"].mean()) if n_purchasers > 0 else 0.0
        net_aov = float(purchasers["net_checkout_order_value"].mean()) if n_purchasers > 0 else 0.0

        rev_per_visitor = retained_rev_total / n_users
        profit_per_visitor = profit_total / n_users
        purchaser_refund_rate = n_refunds / n_purchasers if n_purchasers > 0 else 0.0
        refund_incidence = n_refunds / n_users

        return {
            "total_users": n_users,
            "purchasers": n_purchasers,
            "refunds": n_refunds,
            "retained_revenue_total": retained_rev_total,
            "contribution_profit_total": profit_total,
            "retained_revenue_per_visitor": rev_per_visitor,
            "contribution_profit_per_visitor": profit_per_visitor,
            "gross_aov": gross_aov,
            "net_aov": net_aov,
            "purchaser_refund_rate": purchaser_refund_rate,
            "refund_incidence_per_visitor": refund_incidence
        }

    ctrl_stats = group_stats(ctrl)
    trt_stats = group_stats(trt)

    diff = {
        "retained_revenue_per_visitor_diff": trt_stats["retained_revenue_per_visitor"] - ctrl_stats["retained_revenue_per_visitor"],
        "contribution_profit_per_visitor_diff": trt_stats["contribution_profit_per_visitor"] - ctrl_stats["contribution_profit_per_visitor"],
        "gross_aov_diff": trt_stats["gross_aov"] - ctrl_stats["gross_aov"],
        "net_aov_diff": trt_stats["net_aov"] - ctrl_stats["net_aov"],
        "purchaser_refund_rate_diff": trt_stats["purchaser_refund_rate"] - ctrl_stats["purchaser_refund_rate"],
        "refund_incidence_diff": trt_stats["refund_incidence_per_visitor"] - ctrl_stats["refund_incidence_per_visitor"]
    }

    return {
        "control": ctrl_stats,
        "treatment": trt_stats,
        "difference": diff
    }


def bootstrap_mean_difference(
    control_values: np.ndarray,
    treatment_values: np.ndarray,
    rng: np.random.Generator,
    repetitions: int = BOOTSTRAP_REPETITIONS
) -> Tuple[float, float, float]:
    """
    Compute non-parametric bootstrap confidence interval for difference in means (Treatment - Control).
    Returns (point_difference, lower_bound, upper_bound).
    """
    control_vals = np.asarray(control_values, dtype=float)
    treatment_vals = np.asarray(treatment_values, dtype=float)

    if len(control_vals) == 0 or len(treatment_vals) == 0:
        raise ValueError("Both groups must contain observations.")

    n_ctrl = len(control_vals)
    n_trt = len(treatment_vals)

    diffs = np.empty(repetitions)

    for i in range(repetitions):
        c_sample = rng.choice(control_vals, size=n_ctrl, replace=True)
        t_sample = rng.choice(treatment_vals, size=n_trt, replace=True)
        diffs[i] = t_sample.mean() - c_sample.mean()

    lower_bound, upper_bound = np.percentile(diffs, [2.5, 97.5])
    point_diff = float(treatment_vals.mean() - control_vals.mean())

    return point_diff, float(lower_bound), float(upper_bound)


def run_monetary_bootstraps(
    df: pd.DataFrame,
    seed: int = SEED_BOOTSTRAP,
    repetitions: int = BOOTSTRAP_REPETITIONS
) -> Dict[str, Dict[str, float]]:
    """
    Run 10,000-replication bootstrap for all continuous monetary metrics.
    """
    ctrl = df[df["variant"] == "Control"]
    trt = df[df["variant"] == "Treatment"]

    ctrl_purchasers = ctrl[ctrl["purchase_flag"] == 1]
    trt_purchasers = trt[trt["purchase_flag"] == 1]

    rng = np.random.default_rng(seed)

    metrics = {
        "retained_revenue_per_visitor": (
            ctrl["retained_revenue"].to_numpy(),
            trt["retained_revenue"].to_numpy()
        ),
        "contribution_profit_per_visitor": (
            ctrl["contribution_profit"].to_numpy(),
            trt["contribution_profit"].to_numpy()
        ),
        "gross_aov": (
            ctrl_purchasers["pre_discount_order_value"].to_numpy(),
            trt_purchasers["pre_discount_order_value"].to_numpy()
        ),
        "net_aov": (
            ctrl_purchasers["net_checkout_order_value"].to_numpy(),
            trt_purchasers["net_checkout_order_value"].to_numpy()
        )
    }

    results = {}
    for metric_name, (c_vals, t_vals) in metrics.items():
        diff, low, high = bootstrap_mean_difference(c_vals, t_vals, rng, repetitions)
        results[metric_name] = {
            "difference": diff,
            "lower_bound": low,
            "upper_bound": high
        }

    return results


def calculate_refund_guardrail_ci(
    df: pd.DataFrame,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Compute 95% Newcombe confidence interval for the purchaser refund rate difference.
    """
    ctrl_purchasers = df[(df["variant"] == "Control") & (df["purchase_flag"] == 1)]
    trt_purchasers = df[(df["variant"] == "Treatment") & (df["purchase_flag"] == 1)]

    n1 = len(trt_purchasers)
    k1 = int(trt_purchasers["refund_flag"].sum())
    n2 = len(ctrl_purchasers)
    k2 = int(ctrl_purchasers["refund_flag"].sum())

    rate_trt = k1 / n1
    rate_ctrl = k2 / n2
    diff = rate_trt - rate_ctrl

    low, high = confint_proportions_2indep(
        count1=k1,
        nobs1=n1,
        count2=k2,
        nobs2=n2,
        method="newcomb",
        compare="diff",
        alpha=alpha
    )

    rejection_triggered = low > REFUND_GUARDRAIL
    guardrail_satisfied = high <= REFUND_GUARDRAIL

    return {
        "treatment_refund_rate": float(rate_trt),
        "control_refund_rate": float(rate_ctrl),
        "difference": float(diff),
        "lower_bound": float(low),
        "upper_bound": float(high),
        "guardrail_threshold": REFUND_GUARDRAIL,
        "rejection_triggered": bool(rejection_triggered),
        "guardrail_satisfied": bool(guardrail_satisfied)
    }
