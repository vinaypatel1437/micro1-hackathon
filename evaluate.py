# evaluate.py
import time
import json
from pathlib import Path
from tabulate import tabulate
from baseline import run_baseline_on_case
from agent_workflow import run_agent_on_case

def run_benchmark():
    case_dirs = sorted([d for d in Path("data").iterdir() if d.is_dir()])
    
    baseline_correct = 0
    agent_correct = 0
    table_rows = []

    print("🚀 Running Benchmark on 10 Cases (Baseline vs Agent)...\n")

    for c in case_dirs:
        with open(c / "ground_truth.json", "r", encoding="utf-8") as f:
            gt = json.load(f)

        # 1. Run Baseline
        t0 = time.time()
        b_res = run_baseline_on_case(c)
        b_match = (b_res.get("drift_detected") == gt["drift"]) and (b_res.get("drift_type") == gt["type"])
        if b_match: baseline_correct += 1

        # 2. Run Agent (This also creates the trajectory file)
        t0 = time.time()
        a_res = run_agent_on_case(c)
        a_match = (a_res.get("drift_detected") == gt["drift"]) and (a_res.get("drift_type") == gt["type"])
        if a_match: agent_correct += 1

        table_rows.append([
            c.name,
            gt["type"],
            "✅ PASS" if b_match else f"❌ {b_res.get('drift_type')}",
            "✅ PASS" if a_match else f"❌ {a_res.get('drift_type')}"
        ])

    headers = ["Case ID", "Ground Truth", "Baseline Result", "Agent Result"]
    print(tabulate(table_rows, headers=headers, tablefmt="github"))
    print(f"\n📊 Summary Results:")
    total = len(case_dirs) if len(case_dirs) > 0 else 1
    baseline_pct = round((baseline_correct/total)*100)
    agent_pct = round((agent_correct/total)*100)
    print(f"- Baseline Accuracy: {baseline_correct}/{total} ({baseline_pct}%)")
    print(f"- Agent Accuracy:    {agent_correct}/{total} ({agent_pct}%)")

if __name__ == "__main__":
    run_benchmark()