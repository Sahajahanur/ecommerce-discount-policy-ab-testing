"""
Module for core statistical hypothesis testing, confidence intervals, SRM checks, and regressions.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy.stats import chisquare
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep
from statsmodels.stats.multitest import multipletests
import statsmodels.formula.api as smf

from src.config import ALPHA


def run_two_proportion_z_test(
    treatment_purchases: int,
    treatment_users: int,
    control_purchases: int,
    control_users: int,
    alpha: float = ALPHA
) -> Dict[str, Any]:
    """
    Perform two-sided two-proportion z-test comparing Treatment vs Control conversion.
    """
    # Using [treatment_purchases, control_purchases] gives positive z-statistic for treatment lift
    count = np.array([treatment_purchases, control_purchases])
    nobs = np.array([treatment_users, control_users])

    z_stat, p_val = proportions_ztest(count=count, nobs=nobs, alternative="two-sided")

    control_rate = control_purchases / control_users
    treatment_rate = treatment_purchases / treatment_users
    absolute_lift = treatment_rate - control_rate
    relative_lift = absolute_lift / control_rate

    return {
        "control_rate": float(control_rate),
        "treatment_rate": float(treatment_rate),
        "absolute_lift": float(absolute_lift),
        "relative_lift": float(relative_lift),
        "z_statistic": float(z_stat),
        "p_value": float(p_val),
        "significant": bool(p_val < alpha)
    }


def calculate_newcombe_confidence_interval(
    treatment_purchases: int,
    treatment_users: int,
    control_purchases: int,
    control_users: int,
    alpha: float = ALPHA
) -> Tuple[float, float]:
    """
    Compute 95% Newcombe/Wilson score hybrid confidence interval for proportion difference (Treatment - Control).
    """
    ci_lower, ci_upper = confint_proportions_2indep(
        count1=treatment_purchases,
        nobs1=treatment_users,
        count2=control_purchases,
        nobs2=control_users,
        method="newcomb",
        compare="diff",
        alpha=alpha
    )
    return float(ci_lower), float(ci_upper)


def check_sample_ratio_mismatch(
    control_count: int,
    treatment_count: int,
    expected_ratio: Tuple[float, float] = (0.5, 0.5),
    alpha: float = 0.001
) -> Dict[str, Any]:
    """
    Check for Sample Ratio Mismatch (SRM) using chi-square goodness-of-fit test.
    """
    observed = [control_count, treatment_count]
    total = sum(observed)
    expected = [total * expected_ratio[0], total * expected_ratio[1]]

    chi2_stat, p_val = chisquare(f_obs=observed, f_exp=expected)

    return {
        "chi2_statistic": float(chi2_stat),
        "p_value": float(p_val),
        "srm_detected": bool(p_val < alpha)
    }


def compute_standardized_mean_difference(
    treatment_vals: np.ndarray,
    control_vals: np.ndarray
) -> float:
    """
    Compute Cohen's d / Standardized Mean Difference (SMD) between two groups.
    SMD = (mean_treatment - mean_control) / sqrt((var_treatment + var_control) / 2)
    """
    mean_diff = np.mean(treatment_vals) - np.mean(control_vals)
    pooled_var = (np.var(treatment_vals, ddof=1) + np.var(control_vals, ddof=1)) / 2.0
    if pooled_var <= 0:
        return 0.0
    return float(mean_diff / np.sqrt(pooled_var))


def check_baseline_balance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluate balance across baseline pre-treatment covariates.
    Returns table of SMDs.
    """
    ctrl = df[df["variant"] == "Control"]
    trt = df[df["variant"] == "Treatment"]

    features = {
        "Cart value": (trt["cart_value"].to_numpy(), ctrl["cart_value"].to_numpy()),
        "Returning customer": (
            (trt["customer_type"] == "returning").astype(float).to_numpy(),
            (ctrl["customer_type"] == "returning").astype(float).to_numpy()
        ),
        "Mobile": (
            (trt["device_type"] == "mobile").astype(float).to_numpy(),
            (ctrl["device_type"] == "mobile").astype(float).to_numpy()
        ),
        "Desktop": (
            (trt["device_type"] == "desktop").astype(float).to_numpy(),
            (ctrl["device_type"] == "desktop").astype(float).to_numpy()
        ),
        "Tablet": (
            (trt["device_type"] == "tablet").astype(float).to_numpy(),
            (ctrl["device_type"] == "tablet").astype(float).to_numpy()
        ),
        "Paid traffic": (
            (trt["traffic_source"] == "paid").astype(float).to_numpy(),
            (ctrl["traffic_source"] == "paid").astype(float).to_numpy()
        ),
        "Organic traffic": (
            (trt["traffic_source"] == "organic").astype(float).to_numpy(),
            (ctrl["traffic_source"] == "organic").astype(float).to_numpy()
        ),
        "Email traffic": (
            (trt["traffic_source"] == "email").astype(float).to_numpy(),
            (ctrl["traffic_source"] == "email").astype(float).to_numpy()
        )
    }

    records = []
    for name, (t_vals, c_vals) in features.items():
        smd = compute_standardized_mean_difference(t_vals, c_vals)
        records.append({
            "feature": name,
            "control_mean": float(np.mean(c_vals)),
            "treatment_mean": float(np.mean(t_vals)),
            "SMD": smd,
            "absolute_SMD": abs(smd)
        })

    balance_df = pd.DataFrame(records)
    return balance_df


def apply_holm_bonferroni(
    p_values: List[float],
    alpha: float = ALPHA
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply Holm-Bonferroni step-down multiplicity correction.
    Returns (reject_array, corrected_p_values).
    """
    reject, pvals_corrected, _, _ = multipletests(
        p_values,
        alpha=alpha,
        method="holm"
    )
    return reject, pvals_corrected


def run_logistic_regression(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Fit multivariable logistic regression adjusting for pre-treatment baseline characteristics.
    """
    model = smf.logit(
        "purchase_flag ~ C(variant, Treatment('Control')) + log_cart_value "
        "+ C(customer_type, Treatment('new')) + C(device_type, Treatment('desktop')) "
        "+ C(traffic_source, Treatment('organic'))",
        data=df
    ).fit(disp=False)

    trt_param_name = "C(variant, Treatment('Control'))[T.Treatment]"
    coef = float(model.params[trt_param_name])
    se = float(model.bse[trt_param_name])
    p_val = float(model.pvalues[trt_param_name])
    odds_ratio = float(np.exp(coef))

    ci_low = float(np.exp(coef - 1.95996 * se))
    ci_high = float(np.exp(coef + 1.95996 * se))

    return {
        "converged": bool(model.mle_retvals["converged"]),
        "treatment_coef": coef,
        "treatment_se": se,
        "treatment_p_value": p_val,
        "odds_ratio": odds_ratio,
        "or_ci_lower": ci_low,
        "or_ci_upper": ci_high,
        "pseudo_r2": float(model.prsquared)
    }
