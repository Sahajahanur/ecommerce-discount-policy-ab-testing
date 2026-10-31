# Data Dictionary: Synthetic E-Commerce Discount A/B Testing Dataset

> [!IMPORTANT]
> **Synthetic Data Disclosure**: This dataset (`data/synthetic/discount_ab_test_users.csv`) is completely synthetic and was algorithmically generated for educational, research, and portfolio demonstration purposes. It does not represent real customer transactions, proprietary platform metrics, or actual commercial operations. Never claim or interpret these records as real-world consumer behavior.

---

## 1. Dataset Overview

- **File Path**: `data/synthetic/discount_ab_test_users.csv`
- **Total Rows**: 70,000 records (exactly 35,000 Control, 35,000 Treatment)
- **Total Columns**: 30 columns
- **Unit of Randomization**: `user_id` (1 row per unique visitor under the Intention-To-Treat / ITT framework)
- **Experiment Window**: 28 calendar days starting `2026-01-01`
- **Missing / Null Values**: 0 across all columns
- **Random Seeds Used**:
  - Calibration: `2025`
  - Population & Outcome Simulation: `2026`
  - Bootstrap Resampling: `2027`

---

## 2. Column Specifications

The table below describes all 30 fields in the exported CSV dataset:

| Column Name | Data Type | Physical Unit | Allowed / Observed Range | Description & Generation Logic |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | String (`object`) | Identifier | `U000001` to `U070000` | Unique synthetic visitor identifier. Exactly 70,000 unique values. |
| `experiment_id` | String (`object`) | Identifier | `'discount_offer_2026'` | Constant identifier identifying this specific A/B experiment protocol. |
| `assigned_at` | Datetime (`object` / `string`) | Timestamp | `2026-01-01 00:00:00` to `2026-01-28 23:59:59` | Simulated exposure timestamp over the 28-day experimentation period. |
| `variant` | String (`object`) | Categorical | `['Control', 'Treatment']` | Randomized assignment variant. Control = 10% off on ₹999+ basket; Treatment = 15% off on ₹1,499+ basket. |
| `cart_value` | Float (`float64`) | INR (₹) | `[288.02, 10955.42]` | Pre-discount baseline cart value drawn from a lognormal distribution ($\mu = \ln(1800)$, $\sigma = 0.45$). |
| `customer_type` | String (`object`) | Categorical | `['new', 'returning']` | User lifecycle status at arrival (35% probability of returning, 65% new visitor). |
| `device_type` | String (`object`) | Categorical | `['mobile', 'desktop', 'tablet']` | User hardware client type (65% mobile, 28% desktop, 7% tablet). |
| `traffic_source` | String (`object`) | Categorical | `['paid', 'organic', 'email']` | Marketing acquisition channel (50% paid, 35% organic, 15% email). *(Note: See Discrepancy section regarding `PROJECT_GOAL.md`).* |
| `eligible_under_control` | Boolean (`bool`) | Logical | `[True, False]` | Whether `cart_value >= 999.00` (Control eligibility threshold). True for ~90.46% of visitors. |
| `eligible_under_treatment` | Boolean (`bool`) | Logical | `[True, False]` | Whether `cart_value >= 1499.00` (Treatment eligibility threshold). True for ~65.91% of visitors. |
| `eligible_for_offer` | Boolean (`bool`) | Logical | `[True, False]` | Variant-specific eligibility: equal to `eligible_under_control` if `variant == 'Control'`, else `eligible_under_treatment`. |
| `purchase_probability_control` | Float (`float64`) | Probability $[0, 1]$ | `[0.0213, 0.1013]` | Latent counterfactual conversion probability if assigned to Control policy (calibrated logit score). Mean = 5.00%. |
| `purchase_probability_treatment`| Float (`float64`) | Probability $[0, 1]$ | `[0.0213, 0.1346]` | Latent counterfactual conversion probability if assigned to Treatment policy (calibrated logit score). Mean = 6.01%. |
| `purchase_probability` | Float (`float64`) | Probability $[0, 1]$ | `[0.0213, 0.1346]` | Realized latent probability assigned based on randomized `variant`. Mean = 5.50%. |
| `purchase_flag` | Integer (`int64`) | Binary indicator | `[0, 1]` | Realized purchase conversion event (1 = purchase, 0 = no purchase), simulated via Bernoulli trial using `purchase_probability`. |
| `offer_discount_rate` | Float (`float64`) | Ratio $[0, 1]$ | `[0.10, 0.15]` | Nominal discount percentage associated with variant: 0.10 (10%) for Control; 0.15 (15%) for Treatment. |
| `offer_applied` | Integer (`int64`) | Binary indicator | `[0, 1]` | 1 if `purchase_flag == 1` and `eligible_for_offer == True`; 0 otherwise. |
| `pre_discount_order_value` | Float (`float64`) | INR (₹) | `[0.00, 9376.13]` | Gross pre-discount order total for completed purchases (`cart_value` if `purchase_flag == 1`, else 0.00). |
| `discount_amount` | Float (`float64`) | INR (₹) | `[0.00, 1406.42]` | Price discount conceded: `round(pre_discount_order_value * offer_discount_rate, 2)` if `offer_applied == 1`, else 0.00. |
| `net_checkout_order_value` | Float (`float64`) | INR (₹) | `[0.00, 7969.71]` | Net amount billed at checkout: `pre_discount_order_value - discount_amount`. 0.00 for non-purchasers. |
| `refund_flag` | Integer (`int64`) | Binary indicator | `[0, 1]` | Post-purchase return/refund event. Simulated via Bernoulli trial ($p = 0.08$) exclusively among purchasers (`purchase_flag == 1`). Always 0 for non-purchasers. |
| `estimated_cogs` | Float (`float64`) | INR (₹) | `[0.00, 5625.68]` | Cost of goods sold estimated at 60% of `pre_discount_order_value`. 0.00 for non-purchasers. |
| `retained_revenue` | Float (`float64`) | INR (₹) | `[0.00, 7969.71]` | Revenue kept after refund deduction: `net_checkout_order_value` if `refund_flag == 0`, else 0.00. |
| `retained_cogs` | Float (`float64`) | INR (₹) | `[0.00, 5625.68]` | Inventory cost of retained goods: `estimated_cogs` if `refund_flag == 0`, else 0.00 (returned items restocked). |
| `fulfillment_cost` | Float (`float64`) | INR (₹) | `[0.00, 60.00]` | Outbound picking, packing, and courier shipping cost: fixed ₹60.00 for all purchasers; unrecovered on refund. 0.00 for non-purchasers. |
| `payment_processing_fee` | Float (`float64`) | INR (₹) | `[0.00, 159.39]` | Payment gateway fee: `round(net_checkout_order_value * 0.02, 2)`. Incurred on initial checkout and not recovered on refund. |
| `reverse_logistics_cost` | Float (`float64`) | INR (₹) | `[0.00, 80.00]` | Return pickup, inspection, and restocking fee: fixed ₹80.00 if `refund_flag == 1`, else 0.00. |
| `contribution_profit` | Float (`float64`) | INR (₹) | `[-262.02, 2124.64]` | Net marginal profit contribution per user: `retained_revenue - retained_cogs - fulfillment_cost - payment_processing_fee - reverse_logistics_cost`. |
| `basket_value_band` | String (`object`) | Categorical | 4 defined bands | Customer basket segmentation based on pre-discount `cart_value`: `'Below ₹999'`, `'₹999–₹1,498.99'`, `'₹1,499–₹2,499.99'`, `'₹2,500 and above'`. |
| `log_cart_value` | Float (`float64`) | Standardized log | `[-1.8325, 1.8060]` | Covariate for regression: $\ln(\text{cart\_value} / 1800)$. |

---

## 3. Important Calculated Metrics & Denominators

To prevent metric manipulation and misinterpretation, all calculated KPIs adhere to strict statistical denominators:

### A. Primary Conversion Metric
$$\text{Purchase Conversion Rate (ITT)} = \frac{\sum \text{purchase\_flag}}{\text{Total Randomized Visitors in Group}}$$
- **Control**: $1,787 / 35,000 = 5.1057\%$
- **Treatment**: $2,111 / 35,000 = 6.0314\%$
- **Denominator**: All 35,000 randomized users per variant (Intention-To-Treat principle).

### B. Offer Funnel Metrics
- **Offer Eligibility Rate**:
  $$\text{Eligibility Rate} = \frac{\sum \text{eligible\_for\_offer}}{\text{Total Randomized Visitors in Group}}$$
  - Control Denominator: 35,000 visitors ($31,703 / 35,000 = 90.58\%$)
  - Treatment Denominator: 35,000 visitors ($23,002 / 35,000 = 65.72\%$)
- **Offer Application Rate**:
  $$\text{Application Rate} = \frac{\sum \text{offer\_applied}}{\sum \text{eligible\_for\_offer}}$$
  - Evaluated **strictly among eligible visitors**, not all visitors.
  - Control: $1,678 / 31,703 = 5.2929\%$
  - Treatment: $1,688 / 23,002 = 7.3385\%$
- **Take Rate Among Purchasers**:
  $$\text{Offer Share of Orders} = \frac{\sum \text{offer\_applied}}{\sum \text{purchase\_flag}}$$
  - Control: $1,678 / 1,787 = 93.90\%$
  - Treatment: $1,688 / 2,111 = 79.96\%$ (due to users purchasing below ₹1,499 who did not qualify).

### C. Financial & Monetary Metrics
- **Gross Average Order Value (Gross AOV)**:
  $$\text{Gross AOV} = \frac{\sum \text{pre\_discount\_order\_value}}{\sum \text{purchase\_flag}}$$
  - Evaluated **only among purchasers**.
  - Control: ₹2,098.75 | Treatment: ₹2,218.93
- **Net Average Order Value (Net AOV)**:
  $$\text{Net AOV} = \frac{\sum \text{net\_checkout\_order\_value}}{\sum \text{purchase\_flag}}$$
  - Evaluated **only among purchasers**.
  - Control: ₹1,893.95 | Treatment: ₹1,920.55
- **Revenue per Visitor (RPV)**:
  $$\text{RPV} = \frac{\sum \text{retained\_revenue}}{\text{Total Randomized Visitors in Group}}$$
  - Control: ₹3,106,633.69 / 35,000 = ₹88.76 | Treatment: ₹3,717,279.32 / 35,000 = ₹106.21
- **Contribution Profit per Visitor (CPPV)**:
  $$\text{CPPV} = \frac{\sum \text{contribution\_profit}}{\text{Total Randomized Visitors in Group}}$$
  - Control: ₹854,275.55 / 35,000 = ₹24.41 | Treatment: ₹920,164.34 / 35,000 = ₹26.29

### D. Refund Metrics & Guardrail
- **Purchaser Refund Rate (Guardrail Metric)**:
  $$\text{Purchaser Refund Rate} = \frac{\sum \text{refund\_flag}}{\sum \text{purchase\_flag}}$$
  - Evaluated **strictly among purchasers**.
  - Control: $147 / 1,787 = 8.2261\%$
  - Treatment: $168 / 2,111 = 7.9583\%$
  - Delta ($\text{Treatment} - \text{Control}$): $-0.2678$ percentage points.
- **Refund Incidence per Visitor**:
  $$\text{Refund Incidence} = \frac{\sum \text{refund\_flag}}{\text{Total Randomized Visitors in Group}}$$
  - Control: $147 / 35,000 = 0.4200\%$ | Treatment: $168 / 35,000 = 0.4800\%$

---

## 4. Discrepancy Note

- In [PROJECT_GOAL.md](file:///d:/INTERVIEW_PREP/PYTHON/discount-offer-ab-testing/PROJECT_GOAL.md) Section 3, the planned traffic sources were listed as: *(organic, paid, direct, referral)*.
- In the actual synthetic dataset and notebook, the 3 realized traffic sources are: **`paid` (50%), `organic` (35%), and `email` (15%)**.
