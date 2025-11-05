#!/usr/bin/env python3
"""
Test Runner for Simulation

Runs all test cases and generates metrics.
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


def run_test_case(tc_name: str) -> dict:
    """Run a single test case"""
    print(f"\n{'='*60}")
    print(f"Running {tc_name}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        [sys.executable, "simulate_flow.py", "--test-case", tc_name],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return {
        "test_case": tc_name,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "timestamp": datetime.now().isoformat()
    }


def main():
    """Run all test cases"""
    test_cases = ["TC-1", "TC-2", "TC-3", "TC-4"]
    results = []
    
    for tc in test_cases:
        result = run_test_case(tc)
        results.append(result)
        if result["exit_code"] != 0:
            print(f"\n[WARNING] {tc} failed with exit code {result['exit_code']}")
    
    # Save results
    results_file = Path("artifacts") / "test_results.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    passed = sum(1 for r in results if r["exit_code"] == 0)
    failed = len(results) - passed
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()
