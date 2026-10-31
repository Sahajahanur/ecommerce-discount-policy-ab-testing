"""
End-to-end reproducible experiment pipeline.
Coordinates sample size planning, data generation, statistical analysis, bootstrapping, and decision rules.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd

from src.power_analysis import plan_sample_size
from src.calibration import calibrate_parameters
from src.data_generation import generate_experiment_dataset, save_dataset
from src.statistical_testing import (
    run_two_proportion_z_test,
    calculate_newcombe_confidence_interval,
    check_sample_ratio_mismatch,
    check_baseline_balance,
    run_logistic_regression
)
from src.financial_metrics import (
    compute_financial_summary,
    run_monetary_bootstraps,
    calculate_refund_guardrail_ci
)
from src.decision_framework import evaluate_decision_framework


def run_experiment_pipeline(
    dataset_path: Optional[str] = "data/synthetic/discount_ab_test_users.csv",
    force_regenerate: bool = False,
    bootstrap_reps: int = 10_000
) -> Dict[str, Any]:
    """
    Execute the entire A/B testing workflow end-to-end.
    """
    print("=" * 65)
    print("  E-COMMERCE DISCOUNT POLICY A/B TESTING EXPERIMENT PIPELINE")
    print("=" * 65)

    # 1. Sample Size Planning
    print("\n[1/6] Running Sample Size & Statistical Power Planning...")
    power_plan = plan_sample_size()
    print(f"  • Required per group: {power_plan['required_users_per_group']:,} | Planned: {power_plan['planned_users_per_group']:,}")
    print(f"  • Cohen's h: {power_plan['cohens_h']:.5f} | Nominal Power: {power_plan['achieved_power']:.2%}")

    # 2. Calibration
    print("\n[2/6] Calibrating Latent Purchase Probability Model...")
    cal_intercept, cal_sens, cal_diag = calibrate_parameters()
    print(f"  • Intercept: {cal_intercept:.6f} | Incremental Sensitivity: {cal_sens:.6f}")
    print(f"  • Calibrated Control Target: {cal_diag['control_calibrated']:.4%} | Treatment: {cal_diag['treatment_calibrated']:.4%}")

    # 3. Dataset Generation / Loading
    csv_file = Path(dataset_path) if dataset_path else None
    if csv_file and csv_file.exists() and not force_regenerate:
        print(f"\n[3/6] Loading existing dataset from {csv_file}...")
        df = pd.read_csv(csv_file, parse_dates=["assigned_at"])
    else:
        print("\n[3/6] Generating 70,000 synthetic user records...")
        df = generate_experiment_dataset(
            calibrated_intercept=cal_intercept,
            calibrated_sensitivity=cal_sens
        )
        if csv_file:
            save_dataset(df, str(csv_file))
            print(f"  • Dataset saved to {csv_file}")

    print(f"  • Records: {len(df):,} | Unique Users: {df['user_id'].nunique():,}")

    # 4. Primary Statistical Analysis
    print("\n[4/6] Conducting Primary Hypothesis Test (Conversion Rate)...")
    ctrl = df[df["variant"] == "Control"]
    trt = df[df["variant"] == "Treatment"]

    k_ctrl = int(ctrl["purchase_flag"].sum())
    n_ctrl = len(ctrl)
    k_trt = int(trt["purchase_flag"].sum())
    n_trt = len(trt)

    z_results = run_two_proportion_z_test(k_trt, n_trt, k_ctrl, n_ctrl)
    ci_low, ci_high = calculate_newcombe_confidence_interval(k_trt, n_trt, k_ctrl, n_ctrl)
    srm_results = check_sample_ratio_mismatch(n_ctrl, n_trt)
    balance_df = check_baseline_balance(df)

    print(f"  • Control: {z_results['control_rate']:.4%} ({k_ctrl:,}/{n_ctrl:,})")
    print(f"  • Treatment: {z_results['treatment_rate']:.4%} ({k_trt:,}/{n_trt:,})")
    print(f"  • Absolute Lift: {z_results['absolute_lift'] * 100:+.4f} pp | Relative: {z_results['relative_lift'] * 100:+.2f}%")
    print(f"  • Z-statistic: {z_results['z_statistic']:.4f} | P-value: {z_results['p_value']:.8e}")
    print(f"  • 95% Newcombe CI: [{ci_low * 100:+.4f} pp, {ci_high * 100:+.4f} pp]")
    print(f"  • SRM Check: Chi2 = {srm_results['chi2_statistic']:.4f}, p = {srm_results['p_value']:.4f} (Mismatch: {srm_results['srm_detected']})")

    # 5. Financial & Bootstrap Analysis
    print(f"\n[5/6] Performing Monetary Bootstrap Analysis ({bootstrap_reps:,} reps)...")
    fin_summary = compute_financial_summary(df)
    boot_results = run_monetary_bootstraps(df, repetitions=bootstrap_reps)
    refund_ci = calculate_refund_guardrail_ci(df)

    profit_diff = boot_results["contribution_profit_per_visitor"]["difference"]
    profit_low = boot_results["contribution_profit_per_visitor"]["lower_bound"]
    profit_high = boot_results["contribution_profit_per_visitor"]["upper_bound"]

    rev_diff = boot_results["retained_revenue_per_visitor"]["difference"]
    rev_low = boot_results["retained_revenue_per_visitor"]["lower_bound"]
    rev_high = boot_results["retained_revenue_per_visitor"]["upper_bound"]

    print(f"  • Retained Revenue / Visitor Diff: +INR {rev_diff:.2f} (95% CI: [INR {rev_low:.2f}, INR {rev_high:.2f}])")
    print(f"  • Contribution Profit / Visitor Diff: +INR {profit_diff:.2f} (95% CI: [INR {profit_low:.4f}, INR {profit_high:.4f}])")
    print(f"  • Purchaser Refund Rate Diff: {refund_ci['difference'] * 100:+.4f} pp (95% CI: [{refund_ci['lower_bound'] * 100:+.4f} pp, {refund_ci['upper_bound'] * 100:+.4f} pp])")
    print(f"  • Refund Guardrail (+3.0 pp) Satisfied: {refund_ci['guardrail_satisfied']}")

    # 6. Decision Framework Evaluation
    print("\n[6/6] Evaluating Pre-Registered A/B/C Decision Framework...")
    decision = evaluate_decision_framework(
        p_value=z_results["p_value"],
        absolute_conversion_lift=z_results["absolute_lift"],
        profit_ci_lower=profit_low,
        profit_ci_upper=profit_high,
        refund_ci_lower=refund_ci["lower_bound"],
        refund_ci_upper=refund_ci["upper_bound"]
    )

    print("-" * 65)
    print(f"  FINAL EXPERIMENT DECISION : OUTCOME {decision['final_decision']}")
    print(f"  RECOMMENDATION            : {decision['recommendation']}")
    print(f"  RATIONALE                 : {decision['rationale']}")
    print("-" * 65)

    # 7. Logistic Regression secondary check
    print("\n[Secondary] Multivariable Logistic Regression...")
    logit_res = run_logistic_regression(df)
    print(f"  • Adjusted Treatment OR: {logit_res['odds_ratio']:.4f} (95% CI: [{logit_res['or_ci_lower']:.4f}, {logit_res['or_ci_upper']:.4f}], p = {logit_res['treatment_p_value']:.4e})")

    return {
        "power_plan": power_plan,
        "calibration": cal_diag,
        "primary_z_test": z_results,
        "newcombe_ci": (ci_low, ci_high),
        "srm": srm_results,
        "baseline_balance": balance_df,
        "financial_summary": fin_summary,
        "bootstrap": boot_results,
        "refund_guardrail": refund_ci,
        "decision": decision,
        "logistic_regression": logit_res
    }
