"""Researcher-owned ETL feasibility workload.

This is a compact adaptation of the pinned SlopCodeBench ETL sequence. The
official tests and reference implementations remain outside participant
workspaces; this module only creates the visible development substrate and the
held-out transfer checks.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


BASE_SOURCE = r'''#!/usr/bin/env python3
"""Small ETL CLI used by the experience-guided pilot."""
from __future__ import annotations

import argparse
import ast
import json
import operator
import sys
from typing import Any


class ETLError(Exception):
    def __init__(self, code: str, detail: str, path: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.path = path

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "error",
            "error_code": self.code,
            "message": "ETL_ERROR: " + self.detail,
            "path": self.path,
        }


SUPPORTED = {"select", "filter", "map", "rename", "limit"}


def require_dict(value: Any, path: str, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ETLError("SCHEMA_VALIDATION_FAILED", f"{label} must be an object", path)
    return value


def clean_text(value: Any, path: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ETLError("SCHEMA_VALIDATION_FAILED", f"{label} must be a non-empty string", path)
    return value.strip()


def normalize_step(step: Any, index: int) -> dict[str, Any]:
    path = f"pipeline.steps[{index}]"
    step = require_dict(step, path, "step")
    op = clean_text(step.get("op"), path + ".op", "op").lower()
    if op not in SUPPORTED:
        raise ETLError("UNKNOWN_OP", f"unsupported op '{op}'", path + ".op")
    if op == "select":
        columns = step.get("columns")
        if not isinstance(columns, list) or not columns or any(not isinstance(c, str) for c in columns):
            raise ETLError("SCHEMA_VALIDATION_FAILED", "select.columns must be a non-empty array of strings", path + ".columns")
        if len(set(columns)) != len(columns):
            raise ETLError("SCHEMA_VALIDATION_FAILED", "select.columns must not contain duplicates", path + ".columns")
        return {"op": op, "columns": columns}
    if op == "filter":
        return {"op": op, "where": clean_text(step.get("where"), path + ".where", "filter.where")}
    if op == "map":
        return {
            "op": op,
            "as": clean_text(step.get("as"), path + ".as", "map.as"),
            "expr": clean_text(step.get("expr"), path + ".expr", "map.expr"),
        }
    if op == "limit":
        n = step.get("n")
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ETLError("SCHEMA_VALIDATION_FAILED", "limit.n must be an integer >= 0", path + ".n")
        return {"op": op, "n": n}
    if "mapping" in step:
        mapping = step["mapping"]
        if not isinstance(mapping, dict) or not mapping:
            raise ETLError("SCHEMA_VALIDATION_FAILED", "rename.mapping must be a non-empty object", path + ".mapping")
        if any(not isinstance(k, str) or not isinstance(v, str) for k, v in mapping.items()):
            raise ETLError("SCHEMA_VALIDATION_FAILED", "rename.mapping keys and values must be strings", path + ".mapping")
        return {"op": op, "mapping": mapping}
    if "from" not in step or "to" not in step:
        raise ETLError("SCHEMA_VALIDATION_FAILED", "rename requires mapping or from/to", path)
    source = clean_text(step["from"], path + ".from", "rename.from")
    target = clean_text(step["to"], path + ".to", "rename.to")
    return {"op": op, "mapping": {source: target}}


def normalize_request(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ETLError("SCHEMA_VALIDATION_FAILED", "request must be an object", "")
    pipeline = require_dict(payload.get("pipeline"), "pipeline", "pipeline")
    raw_steps = pipeline.get("steps")
    if not isinstance(raw_steps, list):
        raise ETLError("SCHEMA_VALIDATION_FAILED", "pipeline.steps must be an array", "pipeline.steps")
    dataset = payload.get("dataset")
    if not isinstance(dataset, list):
        raise ETLError("SCHEMA_VALIDATION_FAILED", "dataset must be an array", "dataset")
    for i, row in enumerate(dataset):
        if not isinstance(row, dict):
            raise ETLError("SCHEMA_VALIDATION_FAILED", "dataset rows must be objects", f"dataset[{i}]")
    return {"steps": [normalize_step(step, i) for i, step in enumerate(raw_steps)]}


def _eval_expr(expr: str, row: dict[str, Any]) -> Any:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ETLError("BAD_EXPR", f"invalid expression: {exc.msg}", "") from exc

    def visit(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and (node.value is None or isinstance(node.value, (bool, int, float, str))):
            return node.value
        if isinstance(node, ast.Name):
            return row.get(node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.Not, ast.USub, ast.UAdd)):
            value = visit(node.operand)
            if isinstance(node.op, ast.Not):
                return not bool(value)
            if value is None:
                return None
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
            values = [visit(v) for v in node.values]
            if isinstance(node.op, ast.And):
                return all(bool(v) for v in values)
            return any(bool(v) for v in values)
        if isinstance(node, ast.BinOp) and type(node.op) in {ast.Add, ast.Sub, ast.Mult, ast.Div}:
            left, right = visit(node.left), visit(node.right)
            if left is None or right is None:
                return None
            try:
                return {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}[type(node.op)](left, right)
            except ZeroDivisionError:
                return None
            except (TypeError, ValueError) as exc:
                raise ETLError("EXECUTION_FAILED", str(exc), "") from exc
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            left, right = visit(node.left), visit(node.comparators[0])
            if left is None or right is None or type(left) is not type(right):
                return False
            op = node.ops[0]
            try:
                return {
                    ast.Eq: operator.eq, ast.NotEq: operator.ne,
                    ast.Lt: operator.lt, ast.LtE: operator.le,
                    ast.Gt: operator.gt, ast.GtE: operator.ge,
                }[type(op)](left, right)
            except KeyError as exc:
                raise ETLError("BAD_EXPR", "unsupported comparison", "") from exc
        raise ETLError("BAD_EXPR", "unsupported expression form", "")

    return visit(tree)


def execute_steps(steps: list[dict[str, Any]], dataset: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [dict(row) for row in dataset]
    for i, step in enumerate(steps):
        op = step["op"]
        path = f"pipeline.steps[{i}]"
        if op == "select":
            selected = []
            for row in rows:
                item = {}
                for j, column in enumerate(step["columns"]):
                    if column not in row:
                        raise ETLError("MISSING_COLUMN", f"column '{column}' not found in row", f"{path}.columns[{j}]")
                    item[column] = row[column]
                selected.append(item)
            rows = selected
        elif op == "filter":
            try:
                rows = [row for row in rows if isinstance(_eval_expr(step["where"], row), bool) and _eval_expr(step["where"], row)]
            except ETLError as exc:
                if not exc.path:
                    exc.path = path + ".where"
                raise
        elif op == "map":
            mapped = []
            for row in rows:
                row = dict(row)
                try:
                    row[step["as"]] = _eval_expr(step["expr"], row)
                except ETLError as exc:
                    if not exc.path:
                        exc.path = path + ".expr"
                    raise
                mapped.append(row)
            rows = mapped
        elif op == "rename":
            renamed = []
            for row in rows:
                row = dict(row)
                for source, target in step["mapping"].items():
                    if source not in row:
                        raise ETLError("MISSING_COLUMN", f"rename source '{source}' not found in row", f"{path}.mapping.{source}")
                    row[target] = row.pop(source)
                renamed.append(row)
            rows = renamed
        elif op == "limit":
            rows = rows[: step["n"]]
    return rows


def emit(value: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(value, separators=(",", ":")))
    sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(sys.stdin.read())
        normalized = normalize_request(payload)
        if args.execute:
            data = execute_steps(normalized["steps"], payload["dataset"])
            emit({"status": "ok", "data": data, "metrics": {"rows_in": len(payload["dataset"]), "rows_out": len(data)}})
        else:
            emit({"status": "ok", "normalized": normalized})
        return 0
    except json.JSONDecodeError as exc:
        emit(ETLError("SCHEMA_VALIDATION_FAILED", f"invalid JSON input: {exc.msg}", "").as_dict())
        return 1
    except ETLError as exc:
        emit(exc.as_dict())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


PUBLIC_TESTS = r'''import json
import subprocess
import sys
import unittest
from pathlib import Path


CLI = [sys.executable, str(Path(__file__).parents[1] / "etl_pipeline.py")]


def run(payload, execute=False):
    command = CLI + (["--execute"] if execute else [])
    result = subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True)
    return result.returncode, json.loads(result.stdout)


class Checkpoint12Visible(unittest.TestCase):
    def test_normalizes_trimmed_rename(self):
        code, out = run({"pipeline": {"steps": [{"op": " rename ", "from": " amount ", "to": " price "}]}, "dataset": []})
        self.assertEqual(code, 0)
        self.assertEqual(out["normalized"]["steps"], [{"op": "rename", "mapping": {"amount": "price"}}])

    def test_normalizes_and_drops_unknown_fields(self):
        code, out = run({"pipeline": {"steps": [{"op": " MAP ", "as": " total ", "expr": " price * qty ", "note": "drop"}]}, "dataset": []})
        self.assertEqual(code, 0)
        self.assertEqual(out["normalized"]["steps"], [{"op": "map", "as": "total", "expr": "price * qty"}])

    def test_rejects_unknown_operation(self):
        code, out = run({"pipeline": {"steps": [{"op": "TRANSPOSE"}]}, "dataset": []})
        self.assertEqual(code, 1)
        self.assertEqual(out["error_code"], "UNKNOWN_OP")

    def test_executes_map_filter_limit(self):
        code, out = run({"pipeline": {"steps": [
            {"op": "map", "as": "total", "expr": "price * qty"},
            {"op": "filter", "where": "total >= 10"},
            {"op": "limit", "n": 1},
        ]}, "dataset": [{"id": 1, "price": 5, "qty": 2}, {"id": 2, "price": 9, "qty": 2}]}, execute=True)
        self.assertEqual(code, 0)
        self.assertEqual(out["data"], [{"id": 1, "price": 5, "qty": 2, "total": 10}])

    def test_limit_zero_is_empty(self):
        code, out = run({"pipeline": {"steps": [{"op": "limit", "n": 0}]}, "dataset": [{"id": 1}]}, execute=True)
        self.assertEqual(code, 0)
        self.assertEqual(out["data"], [])

    def test_missing_select_column_is_reported(self):
        code, out = run({"pipeline": {"steps": [{"op": "select", "columns": ["missing"]}]}, "dataset": [{"id": 1}]}, execute=True)
        self.assertEqual(code, 1)
        self.assertEqual(out["error_code"], "MISSING_COLUMN")


if __name__ == "__main__":
    unittest.main()
'''


TRANSFER_HIDDEN_TESTS = [
    {
        "name": "first_match_and_otherwise",
        "payload": {
            "pipeline": {"steps": [{"op": "branch", "branches": [
                {"id": "cheap", "when": "price < 20", "steps": [{"op": "map", "as": "tag", "expr": '"cheap"'}]},
                {"id": "otherwise", "when": "otherwise", "steps": [{"op": "map", "as": "tag", "expr": '"premium"'}]},
            ]}]},
            "dataset": [{"id": 1, "price": 10}, {"id": 2, "price": 25}, {"id": 3, "price": 5}],
        },
        "expected": [{"id": 1, "price": 10, "tag": "cheap"}, {"id": 3, "price": 5, "tag": "cheap"}, {"id": 2, "price": 25, "tag": "premium"}],
    },
    {
        "name": "first_match_wins_and_unmatched_drop",
        "payload": {
            "pipeline": {"steps": [{"op": "branch", "branches": [
                {"id": "high", "when": "price >= 20", "steps": [{"op": "map", "as": "tag", "expr": '"high"'}]},
                {"id": "mid", "when": "price >= 10", "steps": [{"op": "map", "as": "tag", "expr": '"mid"'}]},
            ]}]},
            "dataset": [{"id": 1, "price": 25}, {"id": 2, "price": 15}, {"id": 3, "price": 5}],
        },
        "expected": [{"id": 1, "price": 25, "tag": "high"}, {"id": 2, "price": 15, "tag": "mid"}],
    },
    {
        "name": "branch_nested_filter_and_limit",
        "payload": {
            "pipeline": {"steps": [{"op": "branch", "branches": [
                {"when": "kind == \"a\"", "steps": [{"op": "filter", "where": "value > 0"}, {"op": "limit", "n": 1}]},
                {"when": "otherwise", "steps": []},
            ]}]},
            "dataset": [{"id": 1, "kind": "a", "value": 1}, {"id": 2, "kind": "a", "value": 2}, {"id": 3, "kind": "b", "value": 3}],
        },
        "expected": [{"id": 1, "kind": "a", "value": 1}, {"id": 3, "kind": "b", "value": 3}],
    },
]


TASKS = {
    "dev-normalization": {
        "title": "Repair the checkpoint-1 normalization regression",
        "requirement": "The current CLI must normalize a rename from/to pair by trimming both field names, while preserving the existing select, map, and error behavior. Run the visible tests, inspect the affected source, make a narrow repair, and verify a targeted rename case.",
        "variant": "rename-trim-bug",
    },
    "dev-execution": {
        "title": "Repair the checkpoint-2 linear execution regression",
        "requirement": "The current CLI must execute a linear pipeline and honor limit n=0 by returning zero rows. Preserve the earlier normalization behavior. Use a visible test and a targeted probe to localize and verify the repair.",
        "variant": "limit-zero-bug",
    },
    "dev-filter-fresh": {
        "title": "Repair the fresh filter truth regression",
        "requirement": "Repair the current linear executor so filter keeps a row only when its predicate evaluates to boolean true. Preserve the earlier checkpoint behavior. Run the visible tests, inspect the predicate implementation, and verify a targeted filter probe before reporting completion.",
        "variant": "filter-truth-bug",
    },
    "transfer-branch": {
        "title": "Add the unfamiliar checkpoint-3 branch step",
        "requirement": "Extend the current ETL CLI with a branch step. A branch has a non-empty branches array; each branch has an optional id, a boolean expression in when or the literal otherwise, and nested steps using the existing operations. Rows go to the first matching branch only. An otherwise branch must be last. Execute branch outputs in branch declaration order, preserving row order within each branch; rows with no match are dropped. The normalized form keeps op, branches and merge with strategy concat (default when omitted). Preserve all earlier behavior and error reporting.",
        "variant": "checkpoint-2",
    },
}


def write_workspace(root: Path, task_id: str, *, history: Path | None = None) -> None:
    task = TASKS[task_id]
    root.mkdir(parents=True, exist_ok=True)
    source = BASE_SOURCE
    if task["variant"] == "rename-trim-bug":
        source = source.replace(
            'source = clean_text(step["from"], path + ".from", "rename.from")\n    target = clean_text(step["to"], path + ".to", "rename.to")',
            'source = step["from"]\n    target = step["to"]',
        )
    elif task["variant"] == "limit-zero-bug":
        source = source.replace('rows = rows[: step["n"]]', 'rows = rows[: step["n"]] if step["n"] else rows')
    elif task["variant"] == "filter-truth-bug":
        source = source.replace(
            'rows = [row for row in rows if isinstance(_eval_expr(step["where"], row), bool) and _eval_expr(step["where"], row)]',
            'rows = [row for row in rows if _eval_expr(step["where"], row) is not None]',
        )
    (root / "etl_pipeline.py").write_text(source)
    (root / "etl_pipeline.py").chmod(0o755)
    (root / "TASK.md").write_text(f"# {task['title']}\n\n{task['requirement']}\n")
    tests = root / "tests"
    tests.mkdir(exist_ok=True)
    (tests / "test_public.py").write_text(PUBLIC_TESTS)
    if history is not None:
        target = root / "history"
        target.mkdir(exist_ok=True)
        for item in history.iterdir():
            if item.is_file():
                shutil.copy2(item, target / item.name)


def write_examiner_tests(root: Path) -> None:
    """Write held-out tests outside the participant workspace."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "hidden_cases.json").write_text(json.dumps(TRANSFER_HIDDEN_TESTS, indent=2))


def source_hash(root: Path) -> str:
    import hashlib

    return hashlib.sha256((root / "etl_pipeline.py").read_bytes()).hexdigest()
