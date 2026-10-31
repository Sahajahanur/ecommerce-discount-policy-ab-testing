# E-commerce Discount Offer Optimization — A/B Testing

**An end-to-end Python A/B Testing project evaluating two e-commerce discount policies using statistical hypothesis testing, bootstrap confidence intervals, logistic regression and profitability analysis.**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Statistics](https://img.shields.io/badge/Statistics-A%2FB%20Testing-orange)
![Pytest](https://img.shields.io/badge/Pytest-23%20Passed-brightgreen)
![Dataset](https://img.shields.io/badge/Dataset-70K%20Synthetic%20Users-blueviolet)

> **Simulation disclosure:** All customers, purchases and financial figures in this project are synthetic and generated using predefined assumptions. This is an independent portfolio project, not an analysis of real company transactions or actual business performance.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Business Problem](#2-business-problem)
3. [Experiment Design](#3-experiment-design)
4. [Dataset Description](#4-dataset-description)
5. [Tools and Technologies](#5-tools-and-technologies)
6. [Statistical Methodology](#6-statistical-methodology)
7. [Business Metrics](#7-business-metrics)
8. [Results and Findings](#8-results-and-findings)
9. [Customer Segmentation](#9-customer-segmentation)
10. [Logistic Regression](#10-logistic-regression)
11. [Final Business Decision](#11-final-business-decision)
12. [Project Structure](#12-project-structure)
13. [Installation and Execution](#13-installation-and-execution)
14. [Automated Testing](#14-automated-testing)
15. [Limitations](#15-limitations)
16. [Future Improvements](#16-future-improvements)
17. [Author and Contact](#17-author-and-contact)

---

## 1. Project Overview

This project simulates a randomized, two-arm e-commerce A/B experiment to evaluate two discount policies and identify which strategy delivers a better balance between customer conversion and business profitability.

The project covers the experimentation lifecycle:

- Statistical power and sample-size planning.
- Synthetic customer data generation.
- Randomized experiment assignment.
- Data validation and baseline balance checks.
- Hypothesis testing and confidence intervals.
- Revenue, AOV, refund and contribution-profit analysis.
- Customer segmentation and logistic regression.
- Bootstrap estimation and multiple-comparison correction.
- Rule-based business decision-making.
- Reusable Python modules and automated testing.

The final objective is to demonstrate how statistical evidence can be translated into a profit-aware business recommendation.

## 2. Business Problem

E-commerce businesses frequently use discounts to increase purchase conversion.

However, a higher discount does not necessarily generate higher contribution profit. Additional purchases may come with increased discount costs, fulfilment expenses, payment fees and refund exposure.

The business question is:

**Which discount policy generates a better overall business outcome while maintaining acceptable profitability and refund risk?**

The analysis considers five major dimensions:

- Purchase conversion.
- Average Order Value (AOV).
- Retained revenue.
- Contribution profit.
- Customer refunds.

## 3. Experiment Design

Two discount policies are compared:

| Parameter | Control (A) | Treatment (B) |
|---|---:|---:|
| Discount | 10% | 15% |
| Minimum basket value | ₹999 | ₹1,499 |
| Randomized users | 35,000 | 35,000 |
| Allocation | 50% | 50% |

**Experiment configuration:**

- Total sample size: 70,000 simulated users.
- Allocation ratio: 50:50.
- Measurement window: Same checkout session.
- Experiment assignment: Randomized.
- Primary analysis: Intention-to-Treat (ITT).
- Data source: Synthetic data generated using predefined simulation assumptions.

**Important experimental design consideration:**

The Treatment changes both discount percentage and minimum basket threshold. Therefore, this experiment compares two bundled discount policies; it cannot independently identify the effect of changing discount depth versus changing the eligibility threshold.

## 4. Dataset Description

The experiment dataset contains:

- 70,000 unique simulated users.
- 35,000 Control users.
- 35,000 Treatment users.
- 30 columns.

The dataset is generated using predefined random seeds and a logistic purchase-probability model calibrated to target conversion probabilities of 5% for Control and 6% for Treatment.

These are simulation targets, not observed conversion results.

### Important Dataset Columns

| Column | Description |
|---|---|
| `user_id` | Unique customer identifier |
| `experiment_id` | Experiment identifier |
| `assigned_at` | Experiment assignment timestamp |
| `variant` | Control or Treatment |
| `cart_value` | Pre-discount basket value |
| `customer_type` | New or returning customer |
| `device_type` | Mobile, desktop or tablet |
| `traffic_source` | Paid, organic or email |
| `eligible_for_offer` | Eligibility under the assigned policy |
| `purchase_probability` | Simulated purchase probability |
| `purchase_flag` | Simulated purchase outcome (0/1) |
| `offer_applied` | Whether the discount was applied |
| `discount_amount` | Applied discount amount |
| `refund_flag` | Simulated refund outcome (0/1) |
| `retained_revenue` | Revenue retained after refunds |
| `contribution_profit` | Profit after specified variable costs |

The complete column definitions are available in [`docs/data_dictionary.md`](docs/data_dictionary.md).

**Dataset availability:** The generated CSV is intentionally excluded from Git through `.gitignore`. It is stored locally at:

`data/synthetic/discount_ab_test_users.csv`

No real customer or transaction data is used.

## 5. Tools and Technologies

| Technology | Purpose |
|---|---|
| Python 3.10 | Programming and experiment implementation |
| NumPy | Numerical calculations and simulation |
| Pandas | Data manipulation and analysis |
| SciPy | Statistical calculations |
| Statsmodels | Hypothesis testing and logistic regression |
| Matplotlib | Data visualization |
| Jupyter Notebook | Interactive analysis |
| Pytest | Automated testing |
| Git and GitHub | Version control and project hosting |

## 6. Statistical Methodology

The project uses a predefined statistical framework to evaluate conversion differences and business outcomes.

### 6.1 Sample Size and Power Analysis

| Parameter | Value |
|---|---:|
| Planning Control conversion | 5.0% |
| Planning Treatment conversion | 5.5% |
| Minimum Detectable Effect (MDE) | 0.5 percentage points |
| Significance level (Alpha) | 0.05 |
| Target statistical power | 80% |
| Cohen's h | 0.02242 |
| Required users per group | 31,218 |
| Planned users per group | 35,000 |
| Achieved nominal power | 84.29% |

### 6.2 Hypothesis Testing

**Null Hypothesis (H₀):**

There is no difference between the actual purchase conversion rates of Control and Treatment.

H₀: pA = pB

**Alternative Hypothesis (H₁):**

There is a difference between the actual purchase conversion rates of Control and Treatment.

H₁: pA ≠ pB

A two-sided two-proportion Z-test is used with a significance level of 0.05.

### 6.3 Statistical Techniques Applied

- Statistical power and sample-size calculation.
- Minimum Detectable Effect (MDE).
- Cohen's h effect size.
- Alpha and hypothesis formulation.
- Two-proportion Z-test.
- P-value interpretation.
- Newcombe/Wilson 95% confidence intervals.
- Bootstrap confidence intervals using 10,000 repetitions.
- Holm multiple-comparison correction.
- Logistic regression.
- Sample Ratio Mismatch (SRM) testing.
- Standardized Mean Difference (SMD) for baseline balance.

## 7. Business Metrics

### Conversion Metrics
- Purchase conversion rate.
- Absolute conversion lift.
- Relative conversion lift.

### Revenue Metrics
- Gross revenue.
- Retained revenue.
- Revenue per visitor.
- Gross Average Order Value.
- Net Average Order Value.

### Profitability Metrics
- Estimated Cost of Goods Sold (COGS).
- Fulfilment cost.
- Payment processing fee.
- Reverse logistics cost.
- Contribution profit.
- Contribution profit per visitor.

### Refund and Customer Metrics
- Offer eligibility rate.
- Offer application rate.
- Purchaser refund rate.
- Refund incidence per visitor.

The primary conversion metric follows the Intention-to-Treat principle: all randomized users remain in their originally assigned groups, regardless of offer eligibility or offer application.

## 8. Results and Findings

All results below are calculated from the simulated experiment dataset.

### 8.1 Purchase Conversion — Primary Metric

| Metric | Control | Treatment |
|---|---:|---:|
| Total users | 35,000 | 35,000 |
| Purchasers | 1,787 | 2,111 |
| Conversion rate | 5.1057% | 6.0314% |

**Observed conversion improvement:**

- Absolute lift: +0.9257 percentage points.
- Relative lift: +18.13%.

### 8.2 Statistical Test Results

| Metric | Result |
|---|---:|
| Z-statistic magnitude | 5.3403 |
| P-value | 9.279 × 10⁻⁸ |
| Significance level | 0.05 |
| 95% Newcombe CI | +0.5861 to +1.2657 pp |

The p-value is below 0.05, and the confidence interval excludes zero.

Therefore, we reject the Null Hypothesis and find strong statistical evidence of a difference in conversion rates in favour of Treatment.

**Z-statistic sign convention:** The notebook reports -5.3403 because Control is supplied first, whereas the standalone pipeline reports +5.3403 because the group ordering is reversed. The p-value and statistical conclusion are identical.

### 8.3 Revenue and Profitability Results

| Metric | Control | Treatment |
|---|---:|---:|
| Retained revenue | ₹31.07 lakh | ₹37.17 lakh |
| Retained revenue per visitor | ₹88.76 | ₹106.21 |
| Gross AOV | ₹2,098.75 | ₹2,218.93 |
| Net AOV | ₹1,893.95 | ₹1,920.55 |
| Contribution profit | ₹8.54 lakh | ₹9.20 lakh |
| Contribution profit per visitor | ₹24.41 | ₹26.29 |

### 8.4 Bootstrap Confidence Intervals

10,000 bootstrap repetitions were used to estimate uncertainty around monetary metrics.

| Metric | Treatment − Control | 95% Bootstrap CI |
|---|---:|---:|
| Retained revenue per visitor | +₹17.45 | ₹10.66 to ₹24.29 |
| Contribution profit per visitor | +₹1.88 | ₹0.0329 to ₹3.7717 |
| Gross AOV | +₹120.18 | ₹58.05 to ₹181.43 |
| Net AOV | +₹26.60 | -₹26.51 to ₹79.22 |

**Key observations:**

- Treatment has a positive retained-revenue difference.
- Treatment has a positive estimated contribution-profit difference.
- Gross AOV shows a positive difference.
- Net AOV does not show clear statistical evidence of a difference because its confidence interval includes zero.
- The contribution-profit confidence interval lower bound is very close to zero, indicating a narrow profitability advantage.

AOV is calculated among purchasers only, while visitor-level metrics include all randomized users.

### 8.5 Refund Analysis

| Metric | Control | Treatment |
|---|---:|---:|
| Purchasers | 1,787 | 2,111 |
| Refunds | 147 | 168 |
| Purchaser refund rate | 8.226% | 7.958% |

**Treatment-minus-Control refund-rate difference:**

- Observed difference: -0.2678 percentage points.
- 95% Newcombe CI: -2.0084 to +1.4427 percentage points.
- Predefined refund guardrail: +3 percentage points.

The upper confidence bound is below the +3 percentage-point guardrail. Therefore, the refund guardrail is satisfied.

The confidence interval includes zero, so we cannot conclude that Treatment has a statistically lower purchaser refund rate.

## 9. Customer Segmentation

The experiment evaluates discount performance across four customer dimensions.

| Dimension | Segments |
|---|---|
| Basket value | Below ₹999, ₹999–₹1,498.99, ₹1,499–₹2,499.99, ₹2,500+ |
| Customer type | New, returning |
| Device type | Mobile, desktop, tablet |
| Traffic source | Paid, organic, email |

### Key Segment Findings

- Treatment showed a higher observed conversion rate among customers with baskets of ₹1,499 or more.
- Control performed better in the ₹999–₹1,498.99 basket segment.
- Returning customers showed a larger observed conversion improvement than new customers.
- Treatment showed higher observed conversion across mobile, desktop and tablet users.
- Treatment showed higher observed conversion across paid, organic and email traffic.

Twelve two-sided segment-level tests were performed, followed by Holm correction at alpha 0.05.

**Eight of the twelve comparisons remained statistically significant after Holm correction.**

The middle basket-value segment favours Control because customers in that range qualify for the Control offer but not the Treatment offer. This result reflects the eligibility rules of the two bundled policies.

These subgroup analyses are exploratory. A significant result in one segment and a non-significant result in another does not independently establish that treatment effects differ between those segments.

## 10. Logistic Regression

A multivariable logistic regression model was used as a secondary analysis to evaluate the Treatment effect while adjusting for pre-treatment customer characteristics.

Predictors included:

- Log-transformed cart value.
- Customer type.
- Device type.
- Traffic source.

| Metric | Result |
|---|---:|
| Treatment odds ratio | 1.1960 |
| 95% OR confidence interval | 1.1208–1.2762 |
| Treatment p-value | 6.5887 × 10⁻⁸ |
| Pseudo R-squared | 0.0087 |

After adjustment, Treatment was associated with approximately **19.6% higher purchase odds** than Control.

The confidence interval excludes 1, indicating a statistically significant adjusted association.

An odds ratio is not equivalent to a percentage-point increase in conversion rate.

The model has modest explanatory fit, as reflected by the pseudo R-squared of 0.0087.

This secondary analysis complements but does not replace the primary randomized ITT analysis.

## 11. Final Business Decision

The experiment uses a predefined A/B/C decision framework.

### Outcome C — Reject Treatment

Evaluated first. Triggered if either:

- The upper bound of the contribution-profit difference confidence interval is below ₹0; or
- The lower bound of the purchaser refund-rate difference confidence interval exceeds +3 percentage points.

### Outcome A — Adopt Treatment

Evaluated only if Outcome C is not triggered.

Requires all four conditions:

1. Conversion p-value below 0.05.
2. Absolute conversion lift of at least 0.5 percentage points.
3. Contribution-profit confidence interval lower bound above ₹0.
4. Refund-rate confidence interval upper bound at most +3 percentage points.

### Outcome B — Retain Control / Inconclusive

Applies when neither Outcome C nor Outcome A is triggered.

### Final Simulated Decision

**OUTCOME A — ADOPT TREATMENT B**

All four adoption conditions passed, and neither rejection condition was triggered.

Treatment B (15% discount with a ₹1,499 minimum basket) is recommended under the predefined decision framework for this simulated experiment.

However, the contribution-profit confidence interval lower bound is only ₹0.0329 per visitor. The profitability advantage is positive but narrow.

In a real business setting, this would justify a cautious, staged rollout with continued profitability and refund monitoring rather than assuming a guaranteed commercial benefit.

## 12. Project Structure

```text
ecommerce-discount-policy-ab-testing/
│
├── data/
│   └── synthetic/                  # Generated CSV (not tracked in Git)
│
├── docs/
│   ├── business_findings.md
│   ├── data_dictionary.md
│   └── statistical_methodology.md
│
├── src/
│   ├── __init__.py
│   ├── calibration.py
│   ├── config.py
│   ├── data_generation.py
│   ├── decision_framework.py
│   ├── financial_metrics.py
│   ├── pipeline.py
│   ├── power_analysis.py
│   └── statistical_testing.py
│
├── tests/
│   ├── __init__.py
│   ├── test_data_generation.py
│   ├── test_decision_framework.py
│   ├── test_financial_metrics.py
│   ├── test_power_analysis.py
│   └── test_statistical_testing.py
│
├── discount_offer_ab_testing.ipynb
├── run_pipeline.py
├── PROJECT_GOAL.md
├── PROJECT_STATE.md
├── requirements.txt
└── .gitignore
```

## 13. Installation and Execution

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sahajahanur/ecommerce-discount-policy-ab-testing.git
cd ecommerce-discount-policy-ab-testing
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Prepare the Synthetic Dataset

The CSV is excluded from Git.

The standalone pipeline expects the generated dataset at:

```text
data/synthetic/discount_ab_test_users.csv
```

Before running the pipeline from a fresh clone, generate or place the dataset at this location using the project's synthetic data-generation implementation in `src/data_generation.py`.

The current standalone pipeline loads an existing CSV; it does not automatically generate the dataset.

### Step 5: Run Automated Tests

```bash
pytest -v
```

**Verified development-environment output:**

```text
23 passed in 3.69s
```

### Step 6: Run the Standalone Pipeline

```bash
python run_pipeline.py
```

The verified pipeline executes sample-size planning, calibration, primary hypothesis testing, financial bootstrap analysis, refund guardrail evaluation, the A/B/C decision framework and secondary logistic regression.

**Verified final pipeline decision:**

```text
FINAL EXPERIMENT DECISION : OUTCOME A
RECOMMENDATION            : Adopt Treatment

Pipeline successfully completed with Decision Outcome: A
```

### Step 7: Open the Jupyter Notebook

```bash
jupyter notebook discount_offer_ab_testing.ipynb
```

See the notebook limitation described in Section 15 before attempting a clean-kernel execution.

## 14. Automated Testing

The standalone Python implementation was tested using Pytest.

| Verification | Result |
|---|---:|
| Total tests collected | 23 |
| Tests passed | 23 |
| Tests failed | 0 |
| Test execution time | 3.69 seconds |
| Pytest exit code | 0 |
| Pipeline exit code | 0 |
| Dataset records verified | 70,000 |
| Dataset columns verified | 30 |
| Unique user IDs | 70,000 |

The automated test suite covers:

- Data generation and dataset validation.
- Financial accounting consistency.
- Contribution-profit calculations.
- Bootstrap reproducibility.
- Refund guardrail logic.
- Sample-size and statistical power calculations.
- Two-proportion Z-test.
- Newcombe confidence intervals.
- SRM and baseline balance calculations.
- Holm multiple-comparison correction.
- A/B/C decision framework and decision-rule precedence.

The standalone pipeline was executed successfully, and its key numerical outputs matched the previously executed notebook analysis.

## 15. Limitations

- All customers, purchases and financial figures are synthetic.
- Conversion targets, cost assumptions, refund assumptions and model coefficients are predefined simulation parameters.
- Statistical significance on synthetic data does not establish real-world business impact.
- The experiment compares two bundled policies and cannot isolate the independent effects of discount percentage and minimum basket threshold.
- Segment-level analyses are exploratory.
- The contribution-profit confidence interval lower bound is close to zero.
- Logistic regression has modest explanatory fit.
- The CSV dataset is excluded from Git and must be generated or supplied locally before running the standalone pipeline.
- The Jupyter notebook has a known issue: Cell 30 contains Python source but is saved with Markdown cell metadata. Clean-kernel, top-to-bottom notebook execution has not been verified. The standalone Python pipeline was executed successfully and its numerical results matched the notebook outputs.

## 16. Future Improvements

- Correct the notebook cell metadata and verify complete clean-kernel execution.
- Add a documented one-command synthetic dataset generation workflow for fresh repository clones.
- Test discount depth and minimum basket threshold independently using a factorial experimental design.
- Extend the measurement window to evaluate longer-term refunds and repeat purchases.
- Evaluate segment-level treatment interactions with appropriate statistical uncertainty.
- Add monitoring and sensitivity analysis around the narrow contribution-profit margin.

## 17. Author and Contact

**Sahajahanur Rahman Laskar**

- Email: connectingsrl@gmail.com
- LinkedIn: [Sahajahanur Rahman Laskar](https://www.linkedin.com/in/sahajahanur-laskar/)
- GitHub: [Sahajahanur](https://github.com/Sahajahanur)

**Repository:** [ecommerce-discount-policy-ab-testing](https://github.com/Sahajahanur/ecommerce-discount-policy-ab-testing)

---

*Independent portfolio project using entirely synthetic data. All findings and recommendations are illustrative and must not be represented as actual results from a real e-commerce business.*
