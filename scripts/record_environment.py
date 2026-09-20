"""Record exact local and reused-resource provenance for a pilot."""
from __future__ import annotations

import hashlib
import importlib.metadata as md
import json
import platform
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    model_root = (root / "../weight-consolidation/models/qwen3-4b-4bit").resolve()
    model_manifest = json.loads((root / "../weight-consolidation/resources/model.json").read_text())
    record = {
        "date": "2026-09-20",
        "platform": platform.platform(),
        "python": platform.python_version(),
        "packages": {name: md.version(name) for name in ["mlx", "mlx-lm", "transformers"]},
        "study_git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "uv_lock_sha256": sha256(root / "uv.lock"),
        "model": {
            "path": str(model_root),
            "study_sibling_revision": subprocess.check_output(["git", "-C", str(root / "../weight-consolidation"), "rev-parse", "HEAD"], text=True).strip(),
            "manifest": model_manifest,
        },
        "pinned_sources": {
            "scb_problems": "ef6a9dd13911566b6b01075ca121758c9f7b5c5f",
            "slop_code_bench": "c2a53b46ed7227545951168e1dfeea8a6eec9316",
        },
        "remote_serving": {
            "models_probe": "HTTP 200; qwen3 8B and qwen3.8 27B listed",
            "chat_probe": "HTTP 200; inference response received from qwen3 8B",
            "mutable_state_probe": "HTTP 404 for /engines/v1/training; no training or mutable-state API exposed",
            "user_agent": "experience-guided-investigation/0.1 (local pilot)",
        },
        "participant_boundary": {
            "visible": ["TASK.md", "etl_pipeline.py", "tests/test_public.py", "history/*"],
            "outside_workspace": ["examiner/hidden_cases.json", "official pinned tests and reference implementations"],
        },
    }
    out = root / "evidence/pilot-01/environment.json"
    out.write_text(json.dumps(record, indent=2))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
