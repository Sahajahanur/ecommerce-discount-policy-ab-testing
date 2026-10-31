"""
Unit tests for two-proportion z-tests, Newcombe confidence intervals, SRM, SMD, and Holm correction.
"""

import pytest
import numpy as np
from src.statistical_testing import (
    run_two_proportion_z_test,
    calculate_newcombe_confidence_interval,
    check_sample_ratio_mismatch,
    compute_standardized_mean_difference,
    apply_holm_bonferroni
)


def test_two_proportion_z_test_verified_counts():
    """Verify two-proportion z-test against verified notebook numbers."""
    # Control: 1,787 / 35,000; Treatment: 2,111 / 35,000
    res = run_two_proportion_z_test(
        treatment_purchases=2111,
        treatment_users=35000,
        control_purchases=1787,
        control_users=35000,
        alpha=0.05
    )
    assert pytest.approx(res["control_rate"], abs=1e-5) == 0.051057
    assert pytest.approx(res["treatment_rate"], abs=1e-5) == 0.060314
    assert pytest.approx(res["absolute_lift"], abs=1e-5) == 0.009257
    assert pytest.approx(res["relative_lift"], abs=1e-3) == 0.1813
    assert pytest.approx(res["z_statistic"], abs=1e-2) == 5.3403
    assert res["p_value"] < 1e-6
    assert res["significant"] is True


def test_newcombe_confidence_interval():
    """Verify 95% Newcombe confidence interval excludes 0 and contains observed lift."""
    ci_low, ci_high = calculate_newcombe_confidence_interval(
        treatment_purchases=2111,
        treatment_users=35000,
        control_purchases=1787,
        control_users=35000,
        alpha=0.05
    )
    assert ci_low < ci_high
    assert pytest.approx(ci_low * 100, abs=1e-2) == 0.5861
    assert pytest.approx(ci_high * 100, abs=1e-2) == 1.2657
    assert ci_low <= 0.009257 <= ci_high
    assert ci_low > 0  # Zero is excluded


def test_sample_ratio_mismatch_check():
    """Verify SRM test behaves correctly on balanced and severely mismatched allocations."""
    # Perfect balance
    srm_balanced = check_sample_ratio_mismatch(35000, 35000)
    assert srm_balanced["chi2_statistic"] == 0.0
    assert srm_balanced["p_value"] == 1.0
    assert srm_balanced["srm_detected"] is False

    # Mismatched allocation
    srm_mismatched = check_sample_ratio_mismatch(33000, 37000)
    assert srm_mismatched["p_value"] < 0.001
    assert srm_mismatched["srm_detected"] is True


def test_standardized_mean_difference():
    """Verify SMD calculation."""
    g1 = np.array([10.0, 11.0, 12.0, 10.5])
    g2 = np.array([10.0, 11.0, 12.0, 10.5])
    assert compute_standardized_mean_difference(g1, g2) == 0.0

    g3 = g1 + 2.0
    smd = compute_standardized_mean_difference(g3, g1)
    assert smd > 0


def test_holm_bonferroni_correction():
    """Verify Holm-Bonferroni correction adjusts raw p-values conservatively."""
    raw_p = [0.001, 0.01, 0.04, 0.50]
    reject, adjusted_p = apply_holm_bonferroni(raw_p, alpha=0.05)
    # Adjusted p-values must be >= raw p-values
    assert (adjusted_p >= np.array(raw_p)).all()
    assert reject[0] is True or reject[0] == np.bool_(True)
    assert adjusted_p[-1] == 0.50
