"""External confirmation for the fresh development repair diagnostic."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def evaluate(workspace: Path) -> dict:
    payload = {"pipeline": {"steps": [{"op": "filter", "where": "age > 30"}]}, "dataset": [{"id": 1, "age": 25}, {"id": 2, "age": 35}]}
    result = subprocess.run([sys.executable, "etl_pipeline.py", "--execute"], cwd=workspace, input=json.dumps(payload), text=True, capture_output=True, timeout=20)
    expected = {"status": "ok", "data": [{"id": 2, "age": 35}], "metrics": {"rows_in": 2, "rows_out": 1}}
    try:
        actual = json.loads(result.stdout)
    except json.JSONDecodeError:
        actual = None
    return {"passed": result.returncode == 0 and actual == expected, "returncode": result.returncode, "actual": actual, "expected": expected, "stderr": result.stderr}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = {str(path): evaluate(path) for path in args.workspace}
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
