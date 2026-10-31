"""
Module for pre-experiment sample size planning and statistical power analysis.
"""

from math import ceil
from typing import Dict, Any
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

from src.config import (
    BASELINE_CONTROL_CONVERSION,
    TREATMENT_PLANNING_CONVERSION,
    PLANNING_ALPHA,
    PLANNING_POWER,
    USERS_PER_GROUP
)


def calculate_cohens_h(p1: float, p2: float) -> float:
    """
    Calculate Cohen's h standardized effect size between two proportions.
    h = 2 * arcsin(sqrt(p2)) - 2 * arcsin(sqrt(p1))
    """
    return float(abs(proportion_effectsize(p1, p2)))


def calculate_required_sample_size(
    p1: float = BASELINE_CONTROL_CONVERSION,
    p2: float = TREATMENT_PLANNING_CONVERSION,
    alpha: float = PLANNING_ALPHA,
    power: float = PLANNING_POWER,
    ratio: float = 1.0
) -> int:
    """
    Calculate the minimum required sample size per variant for a two-sided two-proportion z-test.
    """
    effect_size = calculate_cohens_h(p1, p2)
    power_analysis = NormalIndPower()
    required_raw = power_analysis.solve_power(
        effect_size=effect_size,
        power=power,
        alpha=alpha,
        ratio=ratio,
        alternative="two-sided"
    )
    return ceil(required_raw)


def calculate_achieved_power(
    p1: float = BASELINE_CONTROL_CONVERSION,
    p2: float = TREATMENT_PLANNING_CONVERSION,
    n_per_group: int = USERS_PER_GROUP,
    alpha: float = PLANNING_ALPHA,
    ratio: float = 1.0
) -> float:
    """
    Calculate the statistical power achieved by a given planned sample size per group.
    """
    effect_size = calculate_cohens_h(p1, p2)
    power_analysis = NormalIndPower()
    achieved = power_analysis.power(
        effect_size=effect_size,
        nobs1=n_per_group,
        alpha=alpha,
        ratio=ratio,
        alternative="two-sided"
    )
    return float(achieved)


def plan_sample_size() -> Dict[str, Any]:
    """
    Run complete pre-experiment sample size planning protocol.
    """
    effect_size = calculate_cohens_h(
        BASELINE_CONTROL_CONVERSION,
        TREATMENT_PLANNING_CONVERSION
    )
    required_n = calculate_required_sample_size(
        BASELINE_CONTROL_CONVERSION,
        TREATMENT_PLANNING_CONVERSION,
        PLANNING_ALPHA,
        PLANNING_POWER
    )
    achieved_power = calculate_achieved_power(
        BASELINE_CONTROL_CONVERSION,
        TREATMENT_PLANNING_CONVERSION,
        USERS_PER_GROUP,
        PLANNING_ALPHA
    )
    return {
        "baseline_control_rate": BASELINE_CONTROL_CONVERSION,
        "treatment_planning_rate": TREATMENT_PLANNING_CONVERSION,
        "mde_absolute": TREATMENT_PLANNING_CONVERSION - BASELINE_CONTROL_CONVERSION,
        "cohens_h": effect_size,
        "alpha": PLANNING_ALPHA,
        "target_power": PLANNING_POWER,
        "required_users_per_group": required_n,
        "required_total_users": 2 * required_n,
        "planned_users_per_group": USERS_PER_GROUP,
        "planned_total_users": 2 * USERS_PER_GROUP,
        "achieved_power": achieved_power
    }
