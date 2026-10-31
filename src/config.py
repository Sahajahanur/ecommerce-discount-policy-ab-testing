"""
Configuration and locked parameters for the E-commerce Discount Policy A/B Testing project.
All parameters strictly follow the pre-registered specifications in PROJECT_GOAL.md.
"""

# =====================================================================
# 1. RANDOM SEEDS (Strict Reproducibility)
# =====================================================================
SEED_CALIBRATION = 2025
SEED_DATA_GENERATION = 2026
SEED_BOOTSTRAP = 2027

# =====================================================================
# 2. EXPERIMENT DESIGN & SAMPLE SIZE PLANNING
# =====================================================================
TOTAL_USERS = 70_000
USERS_PER_GROUP = 35_000
EXPOSURE_DAYS = 28
START_DATE = "2026-01-01"

BASELINE_CONTROL_CONVERSION = 0.050      # p1 = 5.0%
TREATMENT_PLANNING_CONVERSION = 0.055    # p2 = 5.5% (MDE = +0.5 pp)
PLANNING_ALPHA = 0.05
PLANNING_POWER = 0.80

# Ground-truth simulation targets
TARGET_CONTROL_CONVERSION = 0.050        # 5.0% target for Control
TARGET_TREATMENT_CONVERSION = 0.060      # 6.0% target for Treatment

# =====================================================================
# 3. DISCOUNT POLICIES
# =====================================================================
# Control A
CONTROL_MIN_BASKET = 999.0
CONTROL_DISCOUNT_RATE = 0.10

# Treatment B
TREATMENT_MIN_BASKET = 1499.0
TREATMENT_DISCOUNT_RATE = 0.15

# =====================================================================
# 4. ECONOMIC & FINANCIAL PARAMETERS
# =====================================================================
COGS_RATE = 0.60                         # 60% of pre-discount order value
FULFILLMENT_COST = 60.0                  # Fixed ₹60.0 per purchaser (unrecovered on refund)
PAYMENT_FEE_RATE = 0.02                  # 2% of net checkout order value (unrecovered)
REVERSE_LOGISTICS_COST = 80.0            # Fixed ₹80.0 per refund
REFUND_PROBABILITY = 0.08                # 8% refund probability among purchasers

# Cart value distribution parameters (Lognormal)
CART_MEDIAN = 1800.0
CART_LOG_SIGMA = 0.45

# Latent logit model coefficients
BETA_LOG_CART = 0.25
BETA_RETURNING = 0.25
BETA_PAID = -0.10
BETA_EMAIL = 0.10
BETA_MOBILE = -0.10
BETA_TABLET = 0.00
BASE_DISCOUNT_SENSITIVITY = 0.25

# =====================================================================
# 5. BUSINESS GUARDRAILS & DECISION THRESHOLDS
# =====================================================================
ALPHA = 0.05
PRACTICAL_CONVERSION_THRESHOLD = 0.005   # +0.5 percentage points absolute lift
MIN_ACCEPTABLE_PROFIT_DIFF = 0.0         # ₹0 per randomized visitor
REFUND_GUARDRAIL = 0.03                  # 0.03 (+3.0 pp) max difference in purchaser refund rates
BOOTSTRAP_REPETITIONS = 10_000
