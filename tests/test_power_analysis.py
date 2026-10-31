"""
Unit tests for sample size planning, Cohen's h, and statistical power calculations.
"""

import pytest
from src.power_analysis import (
    calculate_cohens_h,
    calculate_required_sample_size,
    calculate_achieved_power,
    plan_sample_size
)


def test_cohens_h_calculation():
    """Verify Cohen's h matches theoretical arcsine formulation for p1=0.05, p2=0.055."""
    h = calculate_cohens_h(0.05, 0.055)
    assert pytest.approx(h, abs=1e-4) == 0.02242
    # Zero difference should yield h = 0
    assert calculate_cohens_h(0.05, 0.05) == 0.0


def test_required_sample_size():
    """Verify sample size sizing returns 31,218 users per group for 80% power at alpha=0.05."""
    n_required = calculate_required_sample_size(
        p1=0.05,
        p2=0.055,
        alpha=0.05,
        power=0.80
    )
    assert n_required == 31218


def test_achieved_power():
    """Verify nominal power for planned sample size of 35,000 per group exceeds 84%."""
    power = calculate_achieved_power(
        p1=0.05,
        p2=0.055,
        n_per_group=35000,
        alpha=0.05
    )
    assert pytest.approx(power, abs=1e-3) == 0.8429
    assert power >= 0.80


def test_plan_sample_size_structure():
    """Verify complete planning dictionary structure and parameters."""
    plan = plan_sample_size()
    assert plan["planned_total_users"] == 70000
    assert plan["planned_users_per_group"] == 35000
    assert plan["required_users_per_group"] == 31218
    assert plan["achieved_power"] > plan["target_power"]
    assert pytest.approx(plan["mde_absolute"], abs=1e-5) == 0.005
