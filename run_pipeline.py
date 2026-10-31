import sys
import io
from pathlib import Path

# Ensure UTF-8 stdout output across operating systems
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline import run_experiment_pipeline


def main():
    results = run_experiment_pipeline(
        dataset_path="data/synthetic/discount_ab_test_users.csv",
        force_regenerate=False,
        bootstrap_reps=10_000
    )
    decision = results["decision"]["final_decision"]
    print(f"\nPipeline successfully completed with Decision Outcome: {decision}")


if __name__ == "__main__":
    main()
