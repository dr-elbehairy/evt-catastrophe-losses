"""run_all.py — reproduces every number in the paper: 01 core analysis -> 02 reviewer checks -> merge -> figures.
Usage: python run_all.py [--merge-only]"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
if "--merge-only" not in sys.argv:
    for s in ("01_evt_analysis.py", "02_reviewer_checks.py", "02b_mc_median.py"):
        print(">>", s, flush=True); subprocess.run([PY, os.path.join(HERE, s)], check=True)
R = json.load(open(f"{HERE}/evt_results.json")); R["review"] = json.load(open(f"{HERE}/results_review.json"))
json.dump(R, open(f"{HERE}/evt_results.json", "w"), indent=2, default=float); print("merged review -> evt_results.json")
if "--merge-only" not in sys.argv:
    subprocess.run([PY, os.path.join(HERE, "figures.py")], check=True)
