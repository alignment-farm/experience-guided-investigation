"""Prepare and execute the fixed researcher-authored acquisition traces."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from runtime import ToolEnv, render_prompt
from workload import TASKS, source_hash, write_examiner_tests, write_workspace


def trace_actions(task_id: str) -> list[dict]:
    if task_id == "dev-normalization":
        return [
            {"action": "history_search", "pattern": "rename"},
            {"action": "test"},
            {"action": "read", "path": "etl_pipeline.py"},
            {
                "action": "edit",
                "path": "etl_pipeline.py",
                "old": 'source = step["from"]\n    target = step["to"]',
                "new": 'source = clean_text(step["from"], path + ".from", "rename.from")\n    target = clean_text(step["to"], path + ".to", "rename.to")',
            },
            {"action": "test"},
            {
                "action": "probe",
                "payload": {"pipeline": {"steps": [{"op": "rename", "from": " amount ", "to": " price "}]}, "dataset": [{"amount": 3}]},
            },
            {"action": "done", "message": "Visible tests and a trimmed rename execution probe pass."},
        ]
    if task_id == "dev-execution":
        return [
            {"action": "history_search", "pattern": "normalization"},
            {"action": "test"},
            {"action": "read", "path": "etl_pipeline.py"},
            {
                "action": "edit",
                "path": "etl_pipeline.py",
                "old": 'rows = rows[: step["n"]] if step["n"] else rows',
                "new": 'rows = rows[: step["n"]]',
            },
            {"action": "test"},
            {
                "action": "probe",
                "payload": {"pipeline": {"steps": [{"op": "limit", "n": 0}]}, "dataset": [{"id": 1}]},
            },
            {"action": "done", "message": "Earlier normalization work is preserved; limit zero now returns no rows."},
        ]
    raise KeyError(task_id)


def run_trace(task_id: str, workspace: Path, output: Path) -> list[dict]:
    output.mkdir(parents=True, exist_ok=True)
    env = ToolEnv(workspace)
    task_text = TASKS[task_id]["requirement"]
    transcript = ""
    rows: list[dict] = []
    events = []
    started = time.monotonic()
    for index, action in enumerate(trace_actions(task_id)):
        prompt = render_prompt(task_text, transcript)
        target = json.dumps(action, sort_keys=True, separators=(",", ":"))
        result = env.call(action)
        rows.append({"id": f"{task_id}-{index}", "prompt": prompt, "target": target, "action": action, "tool_result": result})
        events.append({"turn": index, "action": action, "result": result})
        transcript += f"\nASSISTANT: {target}\nTOOL: {json.dumps(result, sort_keys=True)}"
    (output / "events.jsonl").write_text("\n".join(json.dumps(event) for event in events) + "\n")
    (output / "transcript.txt").write_text(transcript)
    (output / "summary.json").write_text(json.dumps({
        "task": task_id,
        "status": "complete",
        "steps": len(rows),
        "tool_calls": env.calls,
        "seconds": time.monotonic() - started,
        "source_hash": source_hash(workspace),
    }, indent=2))
    return rows


def add_history(history: Path, task_id: str, run_output: Path) -> None:
    history.mkdir(parents=True, exist_ok=True)
    summary = json.loads((run_output / "summary.json").read_text())
    events = [json.loads(line) for line in (run_output / "events.jsonl").read_text().splitlines() if line.strip()]
    record = {
        "task": task_id,
        "checkpoint": "1" if task_id == "dev-normalization" else "2",
        "status": summary["status"],
        "observations": [
            {"turn": event["turn"], "action": event["action"].get("action"), "ok": event["result"].get("ok"), "returncode": event["result"].get("returncode")}
            for event in events
        ],
        "lesson": "Inspect the source around the failing behavior, test a minimal discriminating input, make the smallest source edit, then rerun both the suite and the probe.",
    }
    (history / f"{task_id}.json").write_text(json.dumps(record, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--participant-cache", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    args.participant_cache.mkdir(parents=True, exist_ok=False)
    acquisition = args.output / "acquisition"
    history = acquisition / "eligible-history"
    history.mkdir(parents=True)
    teacher_rows: list[dict] = []

    dev1_workspace = args.participant_cache / "teacher-dev-normalization"
    write_workspace(dev1_workspace, "dev-normalization")
    teacher_rows.extend(run_trace("dev-normalization", dev1_workspace, acquisition / "dev-normalization"))
    add_history(history, "dev-normalization", acquisition / "dev-normalization")

    dev2_workspace = args.participant_cache / "teacher-dev-execution"
    write_workspace(dev2_workspace, "dev-execution", history=history)
    teacher_rows.extend(run_trace("dev-execution", dev2_workspace, acquisition / "dev-execution"))
    add_history(history, "dev-execution", acquisition / "dev-execution")

    (acquisition / "training.jsonl").write_text("\n".join(json.dumps({"id": row["id"], "prompt": row["prompt"], "target": row["target"]}) for row in teacher_rows) + "\n")
    (acquisition / "teacher-rows.jsonl").write_text("\n".join(json.dumps(row) for row in teacher_rows) + "\n")

    initial = args.output / "initial-transfer-workspace"
    write_workspace(initial, "transfer-branch", history=history)
    examiner = args.output / "examiner"
    write_examiner_tests(examiner)
    for condition in ["ordinary", "learned"]:
        shutil.copytree(initial, args.participant_cache / condition)

    metadata = {
        "protocol": "pilot-v1",
        "tasks": TASKS,
        "acquisition_rows": len(teacher_rows),
        "initial_transfer_source_hash": source_hash(initial),
        "official_problem_revision": "ef6a9dd13911566b6b01075ca121758c9f7b5c5f",
        "official_runner_revision": "c2a53b46ed7227545951168e1dfeea8a6eec9316",
        "participant_boundary": "only initial-transfer-workspace copy; examiner is a sibling outside ToolEnv root",
    }
    (args.output / "design.json").write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
