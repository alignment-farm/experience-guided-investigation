"""Shared participant tools and model loop for the local pilot."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


SYSTEM_INSTRUCTIONS = """You are a software maintenance agent in a fresh session.
Use the available tools to complete the current ETL change. Investigate before
editing: inspect the relevant source and history, run a discriminating public
test or probe, make a narrow source edit, then rerun checks. Do not edit tests,
history, or TASK.md. Reply with exactly one JSON object and no markdown.

Allowed actions:
{"action":"read","path":"etl_pipeline.py"}
{"action":"search","pattern":"text","path":"."}
{"action":"history_search","pattern":"text"}
{"action":"test"}
{"action":"probe","payload":{...}}
{"action":"edit","path":"etl_pipeline.py","old":"exact existing text","new":"replacement text"}
{"action":"done","message":"what was checked"}
"""


def short(value: str, limit: int = 7000) -> str:
    value = value.replace("\x00", "")
    if len(value) <= limit:
        return value
    return value[:limit] + "\n...[truncated]"


class ToolEnv:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.calls = 0

    def _safe(self, relative: str) -> Path:
        path = (self.root / relative).resolve()
        if path != self.root and self.root not in path.parents:
            raise ValueError("path escapes workspace")
        return path

    def call(self, action: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        kind = action.get("action")
        try:
            if kind == "read":
                path = self._safe(str(action.get("path", "")))
                if not path.is_file():
                    return {"ok": False, "error": f"file not found: {action.get('path')}"}
                return {"ok": True, "path": str(path.relative_to(self.root)), "content": short(path.read_text(), 16000)}
            if kind == "search":
                pattern = str(action.get("pattern", ""))
                target = self._safe(str(action.get("path", ".")))
                if not pattern:
                    return {"ok": False, "error": "pattern is empty"}
                files = [target] if target.is_file() else sorted(p for p in target.rglob("*") if p.is_file() and p.stat().st_size < 1_000_000)
                hits: list[str] = []
                for path in files:
                    try:
                        for number, line in enumerate(path.read_text().splitlines(), 1):
                            if pattern.lower() in line.lower():
                                hits.append(f"{path.relative_to(self.root)}:{number}:{line[:300]}")
                    except UnicodeDecodeError:
                        continue
                return {"ok": True, "matches": hits[:80], "truncated": len(hits) > 80}
            if kind == "history_search":
                pattern = str(action.get("pattern", ""))
                target = self.root / "history"
                hits: list[str] = []
                for path in sorted(target.glob("*")) if target.exists() else []:
                    if not path.is_file():
                        continue
                    for number, line in enumerate(path.read_text().splitlines(), 1):
                        if pattern.lower() in line.lower():
                            hits.append(f"{path.name}:{number}:{line[:360]}")
                return {"ok": True, "matches": hits[:80], "truncated": len(hits) > 80}
            if kind == "test":
                return self._run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
            if kind == "probe":
                payload = action.get("payload")
                if not isinstance(payload, dict):
                    return {"ok": False, "error": "probe.payload must be an object"}
                return self._run([sys.executable, "etl_pipeline.py", "--execute"], json.dumps(payload))
            if kind == "edit":
                if action.get("path") != "etl_pipeline.py":
                    return {"ok": False, "error": "only etl_pipeline.py may be edited"}
                path = self._safe("etl_pipeline.py")
                old, new = action.get("old"), action.get("new")
                if not isinstance(old, str) or not isinstance(new, str):
                    return {"ok": False, "error": "edit requires string old and new fields"}
                source = path.read_text()
                count = source.count(old)
                if count != 1:
                    return {"ok": False, "error": f"old text occurs {count} times; edit must identify one exact region"}
                path.write_text(source.replace(old, new, 1))
                return {"ok": True, "edited": "etl_pipeline.py", "bytes": path.stat().st_size}
            if kind == "done":
                return {"ok": True, "done": True, "message": str(action.get("message", ""))}
            return {"ok": False, "error": f"unknown action {kind!r}"}
        except Exception as exc:  # preserve tool failures as evidence, keep loop alive
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    def _run(self, command: list[str], stdin: str | None = None) -> dict[str, Any]:
        started = time.monotonic()
        result = subprocess.run(command, cwd=self.root, input=stdin, text=True, capture_output=True, timeout=20)
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": short(result.stdout, 7000),
            "stderr": short(result.stderr, 3000),
            "seconds": time.monotonic() - started,
        }


def render_prompt(task_text: str, transcript: str) -> str:
    return (
        SYSTEM_INSTRUCTIONS
        + "\n\nCURRENT TASK:\n"
        + task_text
        + "\n\nTRANSCRIPT SO FAR:\n"
        + (transcript or "(no actions yet)")
        + "\n\nReturn the next JSON action."
    )


def parse_action(text: str) -> tuple[dict[str, Any] | None, str]:
    cleaned = text.split("</think>")[-1].strip()
    candidates: list[tuple[int, dict[str, Any]]] = []
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", cleaned):
        try:
            value, end = decoder.raw_decode(cleaned[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "action" in value:
            candidates.append((match.start() + end, value))
    if candidates:
        return candidates[-1][1], cleaned
    return None, cleaned


def format_event(kind: str, **data: Any) -> dict[str, Any]:
    return {"kind": kind, **data}
