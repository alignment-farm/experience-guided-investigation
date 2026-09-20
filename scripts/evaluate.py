"""Evaluate pilot workspaces after participant access has ended."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from workload import source_hash


def run_public(workspace: Path) -> dict:
    started = time.monotonic()
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=workspace, text=True, capture_output=True, timeout=30)
    return {"passed": result.returncode == 0, "returncode": result.returncode, "seconds": time.monotonic() - started, "stdout": result.stdout[-8000:], "stderr": result.stderr[-4000:]}


def run_hidden(workspace: Path, examiner: Path) -> list[dict]:
    cases = json.loads((examiner / "hidden_cases.json").read_text())
    rows = []
    for case in cases:
        result = subprocess.run([sys.executable, "etl_pipeline.py", "--execute"], cwd=workspace, input=json.dumps(case["payload"]), text=True, capture_output=True, timeout=20)
        try:
            actual = json.loads(result.stdout)
        except json.JSONDecodeError:
            actual = None
        expected = {"status": "ok", "data": case["expected"], "metrics": {"rows_in": len(case["payload"]["dataset"]), "rows_out": len(case["expected"])}}
        rows.append({"name": case["name"], "passed": result.returncode == 0 and actual == expected, "returncode": result.returncode, "actual": actual, "expected": expected, "stderr": result.stderr})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--examiner", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    public = run_public(args.workspace)
    hidden = run_hidden(args.workspace, args.examiner)
    report = {"source_hash": source_hash(args.workspace), "public": public, "hidden": hidden, "hidden_passed": sum(row["passed"] for row in hidden), "hidden_total": len(hidden)}
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({"source_hash": report["source_hash"], "public_passed": public["passed"], "hidden_passed": report["hidden_passed"], "hidden_total": report["hidden_total"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
