import json
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
