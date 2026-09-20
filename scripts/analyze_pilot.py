"""Summarize the bounded pilot without selecting on transfer outcomes."""
from __future__ import annotations

import json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text())


def agent_summary(root: Path) -> dict:
    events = [json.loads(line) for line in (root / "events.jsonl").read_text().splitlines() if line.strip()]
    models = [event for event in events if event["kind"] == "model"]
    tools = [event for event in events if event["kind"] == "tool"]
    return {
        "summary": load(root / "summary.json"),
        "model_turns": len(models),
        "invalid_model_actions": sum(event.get("action") is None for event in models),
        "actions": [(event.get("action") or {}).get("action") for event in tools if isinstance(event.get("action"), dict)],
        "edits": sum((event.get("action") or {}).get("action") == "edit" and event.get("result", {}).get("ok") for event in tools),
        "successful_tools": sum(event.get("result", {}).get("ok") for event in tools),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    evidence = root / "evidence/pilot-01"
    training = load(evidence / "adapter-retry-01/summary.json")
    isolation = load(evidence / "isolation.json")
    ordinary = agent_summary(evidence / "ordinary-agent")
    learned = agent_summary(evidence / "learned-agent")
    fresh_base = agent_summary(evidence / "diagnostic-base-agent")
    fresh_adapter = agent_summary(evidence / "diagnostic-adapter-agent")
    ordinary_eval = load(evidence / "ordinary-evaluation.json")
    learned_eval = load(evidence / "learned-evaluation.json")
    fresh_eval = load(evidence / "diagnostic-evaluation.json")
    teacher_transfer = load(evidence / "teacher-transfer/report.json")
    report = {
        "protocol": "pilot-v1",
        "official_benchmark_comparability": False,
        "acquisition": {
            "teacher_rows": 14,
            "teacher_work": "researcher-authored and executed through the same participant tools; no teacher model calls",
            "training": training,
            "isolation": isolation,
        },
        "transfer": {
            "ordinary_continuation": {"agent": ordinary, "evaluation": ordinary_eval},
            "learned_investigation": {"agent": learned, "evaluation": learned_eval},
            "same_initial_source_hash": ordinary["summary"]["workspace_source_hash"] == learned["summary"]["workspace_source_hash"],
            "same_visible_obligations": ordinary_eval["public"]["passed"] and learned_eval["public"]["passed"],
        },
        "fresh_acquisition_diagnostic": {
            "base": {"agent": fresh_base, "evaluation": fresh_eval[".cache/pilot-01/diagnostic-base"]},
            "adapter": {"agent": fresh_adapter, "evaluation": fresh_eval[".cache/pilot-01/diagnostic-adapter"]},
            "interpretation": "Both arms completed the one-line fresh filter repair; adapter-specific improvement is not established because the unchanged base also succeeded.",
        },
        "workload_feasibility": {
            "researcher_authored_transfer": teacher_transfer,
            "interpretation": "The branch change is executable and all three held-out cases pass with a researcher-authored implementation.",
        },
        "findings": [
            "The fixed LoRA run changed the adapter and preserved the base hash; exact load/reset checks passed.",
            "The learned session adopted history search and visible testing early, but did not produce a complete branch patch within 16 turns; repeated multi-site edit outputs were truncated at 384 generated tokens.",
            "The ordinary session also failed to produce a branch patch, stopping after an invalid composite response.",
            "Both base and adapter completed a fresh one-line filter repair, so the pilot establishes a functioning simple repair regime but no adapter advantage.",
            "Zero of three held-out branch cases passed for either transfer arm; this is a demonstrated limitation of the current acquisition/interface regime, not evidence that the neural treatment cannot work with a more suitable patch interface or acquisition target.",
        ],
        "cc1_assessment": "The branch change required residual experience and multi-site reasoning beyond the current source/history archive, but neither arm completed it; no residual experience value was demonstrated.",
        "cc2_assessment": "The learned arm spent more current-task turns without completing the branch change; no repayment or extra-resource comparison is justified.",
        "cc3_assessment": "Both arms used matched checkpoint-2 source and history workspaces. The identical 0/3 outcome does not isolate a policy contribution; the fresh diagnostic shows the shared model/tool regime can repair a smaller change.",
        "cost_notes": "Measured tokens, elapsed time, MLX allocation and adapter bytes are reported; researcher labor, energy, money and deployment startup are unknown.",
    }
    (evidence / "analysis.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
