#!/usr/bin/env python3
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
    source = step["from"]
    target = step["to"]
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
                    row[target] = row.pop(source).strip() if isinstance(row[source], str) and row[source] is not None and row[source].strip() else row.pop(source)
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
