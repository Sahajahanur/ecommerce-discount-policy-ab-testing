# Project Goal: E-commerce Discount Policy A/B Testing

> [!IMPORTANT]
> **Synthetic Data Disclosure**: All data used and generated in this project is strictly synthetic and simulated for demonstration, research, and learning purposes. It does not represent real customer transactions, live platforms, or actual business operations. Never claim real-world results.

---

## 1. Business Objective
Compare two competing e-commerce discount policies using a rigorously designed, reproducible synthetic A/B experiment:
- **Control (Variant A)**: 10% discount on a minimum pre-discount basket size of ₹999.
- **Treatment (Variant B)**: 15% discount on a minimum pre-discount basket size of ₹1,499.

The goal is to determine whether the higher minimum basket threshold paired with a steeper discount (Variant B) drives profitable incremental growth or whether it hurts customer conversion, revenue, and margins compared to the lower threshold policy (Variant A).

---

## 2. Experiment Design & Locked Parameters

### Sample Size & Randomization
- **Total Sample Size**: 70,000 synthetic users.
- **Split Ratio**: 1:1 allocation (exactly 35,000 users per group).
- **Unit of Randomization**: User ID (Intention-To-Treat / ITT framework).
- **Exposure Window**: 28 calendar days starting `2026-01-01`.

### Pre-Experiment Power & Sample Size Planning
- **Baseline Control Conversion ($p_1$)**: 5.0% (0.050).
- **Treatment Planning Conversion ($p_2$)**: 5.5% (0.055) — minimum detectable effect planned.
- **Statistical Power ($1 - \beta$)**: 80% (0.80).
- **Significance Level ($\alpha$)**: 0.05 (two-sided).

### Data Simulation Targets & Seeds
- **Simulated Target Conversion Probabilities**: 
  - Control A: 5.0%
  - Treatment B: 6.0% (simulated ground-truth parameter; observed results will exhibit natural random sampling variance).
- **Random Seeds (Strict Reproducibility)**:
  - Calibration: `2025`
  - Data Generation: `2026`
  - Bootstrapping: `2027`

---

## 3. Metrics & Statistical Evaluation

### Primary Metric
- **Metric**: Purchase Conversion Rate evaluated across **all randomized visitors** (Intention-To-Treat / ITT).
- **Primary Hypothesis Test**: Two-sided two-proportion z-test at $\alpha = 0.05$.
- **Effect Confidence Interval**: 95% Newcombe/Wilson score hybrid confidence interval for the difference between two proportions.

### Secondary Metrics & Extended Analysis
- **Monetary Metrics**:
  - Average Order Value (AOV)
  - Gross Revenue & Retained Revenue (net of discounts & refunds)
  - Contribution Profit per randomized visitor
- **Fulfillment, Eligibility & Funnel Health Metrics**:
  - **Offer Eligibility Rate**: Eligible randomized users divided by all randomized users in the relevant variant (pre-discount basket reaches ₹999 in Control or ₹1,499 in Treatment).
  - **Offer Application Rate**: Users who applied the discount offer divided by eligible randomized users (evaluated separately; eligibility does not imply offer application or final purchase).
  - **Purchaser Refund Rate**: Refunding purchasers divided by all purchasers within the variant.
- **Multivariate & Subgroup Analysis**:
  - Customer segmentation: Customer type (new vs. returning), device type (mobile, desktop, tablet), traffic source (organic, paid, direct, referral), and basket-value bands.
  - Multivariable Logistic Regression to adjust for baseline covariates and detect interaction effects.
- **Monetary Metric Confidence Intervals**:
  - Non-parametric bootstrap estimation with **10,000 replications**.

---

## 4. Business Guardrails & Decision Rules

All decisions are evaluated strictly using pre-registered statistical criteria and confidence intervals for Treatment minus Control ($\Delta = \text{Treatment} - \text{Control}$).

> [!IMPORTANT]
> **Precedence Rule**: **Outcome C takes strict precedence over Outcome A.** If any rejection guardrail is triggered, the treatment is rejected immediately, regardless of conversion lift.

### Precedence-Ordered Decision Outcomes

1. **Outcome C (Reject Treatment — Guardrail Breach / Economic Harm)**:
   *Evaluated first.* Reject Treatment B if either condition is met:
   - The **upper bound** of the 95% bootstrap confidence interval for the contribution profit difference per randomized visitor is below ₹0 ($\text{CI}_{95\%}(\Delta \text{Profit})_{\text{upper}} < 0$), **OR**
   - The **lower bound** of the 95% confidence interval for the purchaser refund-rate difference exceeds $0.03$ ($\text{CI}_{95\%}(\Delta \text{Refund Rate})_{\text{lower}} > 0.03$).

2. **Outcome A (Adopt Treatment — Incrementally Superior & Guarded)**:
   *Evaluated only when Outcome C does not apply.* Adopt Treatment B if **ALL** of the following conditions are simultaneously met:
   - Primary conversion hypothesis two-sided p-value $< 0.05$, **AND**
   - Absolute conversion lift $\Delta p \ge 0.005$ ($+0.5$ percentage points), **AND**
   - The **lower bound** of the 95% bootstrap confidence interval for contribution profit difference is strictly above ₹0 ($\text{CI}_{95\%}(\Delta \text{Profit})_{\text{lower}} > 0$), **AND**
   - The **upper bound** of the 95% confidence interval for the purchaser refund-rate difference is at most $0.03$ ($\text{CI}_{95\%}(\Delta \text{Refund Rate})_{\text{upper}} \le 0.03$).

3. **Outcome B (Retain Control / Inconclusive)**:
   - Applies whenever neither Outcome C nor Outcome A is triggered. Retain Control (Variant A) or declare the test inconclusive due to insufficient statistical evidence, failure to clear practical lift thresholds, or neutral economics.

---

## 5. Final Deliverables
1. **Jupyter Notebook**: Step-by-step, pedagogical, and clean documentation of the experiment lifecycle.
2. **Visualizations**: Publication-grade distribution plots, conversion funnel diagnostics, bootstrap distributions, and effect interval charts.
3. **Test Suite**: Automated unit and integrity tests verifying data sanity, randomization balance, and statistical functions.
4. **Project Documentation**:
   - `README.md`
   - Executive Final Report
   - Data Dictionary
   - Statistical Methodology Documentation
   - Data Science & Product Analytics Interview Defense Guide
