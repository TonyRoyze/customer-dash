import subprocess
import sys
import os
import time

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))

STAGES = [
    ("01_preprocess.py", "Data Preprocessing"),
    ("02_churn_model.py", "Churn Prediction (F1-Optimised)"),
    ("03_revenue_model.py", "Revenue Prediction"),
    ("04_clustering.py", "Customer Clustering")
]


def run_stage(script_name: str, description: str, stage_num: int) -> bool:
    script_path = os.path.join(PIPELINE_DIR, script_name)
    print(f"\n{'━' * 60}")
    print(f"  STAGE {stage_num}/{len(STAGES)} : {description}")
    print(f"  Script: {script_name}")
    print(f"{'━' * 60}\n")

    start = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=PIPELINE_DIR,
        capture_output=False,
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"\n❌ STAGE {stage_num} FAILED ({script_name}) — exit code {result.returncode}")
        return False

    print(f"  ⏱  Completed in {elapsed:.1f}s")
    return True


def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  CUSTOMER ANALYTICS ML PIPELINE".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    total_start = time.time()

    for i, (script, desc) in enumerate(STAGES, 1):
        success = run_stage(script, desc, i)
        if not success:
            print(f"\n🛑 Pipeline halted at stage {i}.")
            sys.exit(1)

    total_elapsed = time.time() - total_start

    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  ✅  ALL STAGES COMPLETE".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"\n  Total runtime: {total_elapsed:.1f}s")
    print()


if __name__ == "__main__":
    main()
