"""
Module for calibrating the latent purchase probability model.
Uses numerical optimization over a reference population to match target ground-truth conversion probabilities.
"""

from typing import Tuple, Dict, Any
import numpy as np
from scipy.optimize import least_squares
from scipy.special import expit

from src.config import (
    SEED_CALIBRATION,
    CART_MEDIAN,
    CART_LOG_SIGMA,
    CONTROL_MIN_BASKET,
    TREATMENT_MIN_BASKET,
    BETA_LOG_CART,
    BETA_RETURNING,
    BETA_PAID,
    BETA_EMAIL,
    BETA_MOBILE,
    BETA_TABLET,
    BASE_DISCOUNT_SENSITIVITY,
    TARGET_CONTROL_CONVERSION,
    TARGET_TREATMENT_CONVERSION
)


def compute_base_scores(
    cart_values: np.ndarray,
    is_returning: np.ndarray,
    device_types: np.ndarray,
    traffic_sources: np.ndarray
) -> np.ndarray:
    """
    Compute customer base logit scores from pre-treatment baseline characteristics.
    """
    is_paid = (traffic_sources == "paid").astype(float)
    is_email = (traffic_sources == "email").astype(float)
    is_mobile = (device_types == "mobile").astype(float)
    is_tablet = (device_types == "tablet").astype(float)
    is_returning_num = is_returning.astype(float)

    base_score = (
        BETA_LOG_CART * np.log(cart_values / CART_MEDIAN)
        + BETA_RETURNING * is_returning_num
        + BETA_PAID * is_paid
        + BETA_EMAIL * is_email
        + BETA_MOBILE * is_mobile
        + BETA_TABLET * is_tablet
    )
    return base_score


def calibrate_parameters(
    reference_size: int = 1_000_000,
    seed: int = SEED_CALIBRATION
) -> Tuple[float, float, Dict[str, Any]]:
    """
    Calibrate model intercept and incremental treatment sensitivity
    to hit target conversion rates of 5.0% (Control) and 6.0% (Treatment).
    """
    rng = np.random.Generator(np.random.PCG64(seed))

    # Reference population generation
    cart_value = rng.lognormal(
        mean=np.log(CART_MEDIAN),
        sigma=CART_LOG_SIGMA,
        size=reference_size
    )
    is_returning = rng.random(reference_size) < 0.35
    device_type = rng.choice(
        ["mobile", "desktop", "tablet"],
        size=reference_size,
        p=[0.65, 0.28, 0.07]
    )
    traffic_source = rng.choice(
        ["paid", "organic", "email"],
        size=reference_size,
        p=[0.50, 0.35, 0.15]
    )

    eligible_under_control = cart_value >= CONTROL_MIN_BASKET
    eligible_under_treatment = cart_value >= TREATMENT_MIN_BASKET

    base_score = compute_base_scores(
        cart_value,
        is_returning,
        device_type,
        traffic_source
    )

    def residuals(parameters):
        intercept, incremental_sensitivity = parameters
        eta_control = (
            intercept
            + base_score
            + BASE_DISCOUNT_SENSITIVITY * eligible_under_control
        )
        eta_treatment = (
            intercept
            + base_score
            + (BASE_DISCOUNT_SENSITIVITY + incremental_sensitivity)
            * eligible_under_treatment
        )
        pred_control = expit(eta_control).mean()
        pred_treatment = expit(eta_treatment).mean()
        return np.array([
            pred_control - TARGET_CONTROL_CONVERSION,
            pred_treatment - TARGET_TREATMENT_CONVERSION
        ])

    result = least_squares(
        residuals,
        x0=[-4.0, 0.5],
        bounds=([-10.0, 0.0], [0.0, 1.0]),
        max_nfev=10000
    )

    calibrated_intercept, calibrated_sensitivity = result.x
    final_res = residuals(result.x)

    diagnostics = {
        "success": bool(result.success),
        "calibrated_intercept": float(calibrated_intercept),
        "calibrated_sensitivity": float(calibrated_sensitivity),
        "control_calibrated": float(TARGET_CONTROL_CONVERSION + final_res[0]),
        "treatment_calibrated": float(TARGET_TREATMENT_CONVERSION + final_res[1]),
        "max_error": float(np.max(np.abs(final_res)))
    }

    return calibrated_intercept, calibrated_sensitivity, diagnostics
