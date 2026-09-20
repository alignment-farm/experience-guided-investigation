"""Run one fresh-session ETL maintenance episode."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

from runtime import ToolEnv, format_event, parse_action, render_prompt
from workload import TASKS, source_hash


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--task", choices=sorted(TASKS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-turns", type=int, default=16)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    events_path = args.output / "events.jsonl"
    events = events_path.open("w")

    def emit(kind: str, **data):
        events.write(json.dumps(format_event(kind, elapsed=time.monotonic() - started, **data)) + "\n")
        events.flush()

    try:
        import mlx.core as mx
        from mlx_lm import load, stream_generate
        from mlx_lm.sample_utils import make_sampler

        model_dir = args.model.resolve()
        model, tokenizer = load(str(model_dir))
        model.freeze()
        adapter_meta = None
        if args.adapter:
            from mlx.utils import tree_unflatten
            from mlx_lm.tuner.utils import linear_to_lora_layers

            linear_to_lora_layers(model, 8, dict(rank=8, scale=2.0, dropout=0.0, keys=["self_attn.q_proj", "self_attn.v_proj"]))
            weights = mx.load(str(args.adapter.resolve()))
            model.update(tree_unflatten(list(weights.items())))
            mx.eval(model.parameters())
            adapter_meta = {"path": str(args.adapter.resolve()), "sha256": sha256(args.adapter.resolve()), "bytes": args.adapter.stat().st_size}
        emit("provenance", python=platform.python_version(), model=str(model_dir), adapter=adapter_meta, task=args.task, workspace_source_hash=source_hash(args.workspace))

        def generate(prompt: str) -> dict:
            rendered = tokenizer.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
            tick = time.monotonic()
            chunks = []
            for chunk in stream_generate(model, tokenizer, rendered, max_tokens=384, sampler=make_sampler(temp=0.0)):
                chunks.append(chunk)
            raw = "".join(chunk.text for chunk in chunks)
            action, cleaned = parse_action(raw)
            return {
                "raw": raw,
                "cleaned": cleaned,
                "action": action,
                "prompt_tokens": len(tokenizer.encode(rendered)),
                "completion_tokens": len(chunks),
                "seconds": time.monotonic() - tick,
            }

        env = ToolEnv(args.workspace)
        task_text = TASKS[args.task]["requirement"]
        transcript = ""
        done = False
        for turn in range(args.max_turns):
            result = generate(render_prompt(task_text, transcript))
            emit("model", turn=turn, **result)
            action = result["action"]
            if action is None:
                tool = {"ok": False, "error": "model did not return a JSON action"}
                emit("tool", turn=turn, action=None, result=tool)
                transcript += f"\nASSISTANT: {result['cleaned']}\nTOOL: {json.dumps(tool, sort_keys=True)}"
                continue
            tool = env.call(action)
            emit("tool", turn=turn, action=action, result=tool)
            transcript += f"\nASSISTANT: {json.dumps(action, sort_keys=True)}\nTOOL: {json.dumps(tool, sort_keys=True)}"
            if action.get("action") == "done" and tool.get("done"):
                done = True
                break
        summary = {
            "status": "complete" if done else "turn_limit",
            "done": done,
            "turns": turn + 1 if 'turn' in locals() else 0,
            "tool_calls": env.calls,
            "seconds": time.monotonic() - started,
            "peak_mlx_bytes": int(mx.get_peak_memory()),
            "workspace_source_hash": source_hash(args.workspace),
        }
        (args.output / "transcript.txt").write_text(transcript)
        (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
        emit("complete", **summary)
        return 0
    except BaseException as exc:
        emit("failure", error=repr(exc))
        (args.output / "summary.json").write_text(json.dumps({"status": "failed", "error": repr(exc), "seconds": time.monotonic() - started}, indent=2))
        raise
    finally:
        events.close()


if __name__ == "__main__":
    raise SystemExit(main())
