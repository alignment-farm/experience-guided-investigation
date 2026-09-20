"""Researcher-authored transfer feasibility check, outside participant access."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from workload import BASE_SOURCE, source_hash, write_workspace


def branch_source() -> str:
    source = BASE_SOURCE.replace(
        'SUPPORTED = {"select", "filter", "map", "rename", "limit"}',
        'SUPPORTED = {"select", "filter", "map", "rename", "limit", "branch"}',
    )
    marker = '    if op == "select":\n'
    normalization = (
        '    if op == "branch":\n'
        '        raw_branches = step.get("branches")\n'
        '        if not isinstance(raw_branches, list) or not raw_branches:\n'
        '            raise ETLError("SCHEMA_VALIDATION_FAILED", "branch.branches must be a non-empty array", path + ".branches")\n'
        '        normalized_branches = []\n'
        '        otherwise_seen = False\n'
        '        for branch_index, branch in enumerate(raw_branches):\n'
        '            branch_path = path + f".branches[{branch_index}]"\n'
        '            branch = require_dict(branch, branch_path, "branch")\n'
        '            when = branch.get("when")\n'
        '            if when == "otherwise":\n'
        '                if otherwise_seen or branch_index != len(raw_branches) - 1:\n'
        '                    raise ETLError("SCHEMA_VALIDATION_FAILED", "otherwise branch must be unique and last", path + ".branches")\n'
        '                otherwise_seen = True\n'
        '            else:\n'
        '                when = clean_text(when, branch_path + ".when", "branch.when")\n'
        '            nested = branch.get("steps")\n'
        '            if not isinstance(nested, list):\n'
        '                raise ETLError("SCHEMA_VALIDATION_FAILED", "branch.steps must be an array", branch_path + ".steps")\n'
        '            item = {"when": when, "steps": [normalize_step(nested_step, nested_index) for nested_index, nested_step in enumerate(nested)]}\n'
        '            if "id" in branch:\n'
        '                item = {"id": clean_text(branch["id"], branch_path + ".id", "branch.id"), **item}\n'
        '            normalized_branches.append(item)\n'
        '        merge = step.get("merge", {}) or {}\n'
        '        merge = require_dict(merge, path + ".merge", "branch.merge")\n'
        '        if merge.get("strategy", "concat") != "concat":\n'
        '            raise ETLError("SCHEMA_VALIDATION_FAILED", "branch.merge.strategy must be concat", path + ".merge.strategy")\n'
        '        return {"op": op, "branches": normalized_branches, "merge": {"strategy": "concat"}}\n'
    )
    source = source.replace(marker, normalization + marker, 1)
    marker = '        if op == "select":\n'
    execution = (
        '        if op == "branch":\n'
        '            merged = []\n'
        '            remaining = list(rows)\n'
        '            for branch in step["branches"]:\n'
        '                selected = []\n'
        '                next_remaining = []\n'
        '                for row in remaining:\n'
        '                    when = branch["when"]\n'
        '                    matches = when == "otherwise" or _eval_expr(when, row) is True\n'
        '                    if matches:\n'
        '                        selected.append(row)\n'
        '                    else:\n'
        '                        next_remaining.append(row)\n'
        '                merged.extend(execute_steps(branch["steps"], selected))\n'
        '                remaining = next_remaining\n'
        '            rows = merged\n'
        '        elif op == "select":\n'
    )
    source = source.replace(marker, execution, 1)
    return source


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--examiner", type=Path, required=True)
    args = parser.parse_args()
    if args.workspace.exists():
        shutil.rmtree(args.workspace)
    write_workspace(args.workspace, "transfer-branch", history=Path("evidence/pilot-01/initial-transfer-workspace/history"))
    (args.workspace / "etl_pipeline.py").write_text(branch_source())
    cases = json.loads((args.examiner / "hidden_cases.json").read_text())
    results = []
    for case in cases:
        result = subprocess.run([sys.executable, "etl_pipeline.py", "--execute"], cwd=args.workspace, input=json.dumps(case["payload"]), text=True, capture_output=True)
        results.append({"name": case["name"], "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    report = {"source_hash": source_hash(args.workspace), "cases": results, "teacher_code": "researcher-authored branch implementation for feasibility only"}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
