"""Verify fresh base loading, adapter loading, and exact adapter reset."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path


def digest(items) -> str:
    import numpy as np
    import mlx.core as mx

    h = hashlib.sha256()
    for name, value in sorted(items):
        h.update(name.encode())
        h.update(str((value.shape, value.dtype)).encode())
        h.update(np.asarray(value.astype(mx.float32)).tobytes())
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    import mlx.core as mx
    from mlx.utils import tree_flatten, tree_unflatten
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler
    from mlx_lm.tuner.utils import linear_to_lora_layers

    model, tokenizer = load(str(args.model.resolve()))
    model.freeze()
    linear_to_lora_layers(model, 8, dict(rank=8, scale=2.0, dropout=0.0, keys=["self_attn.q_proj", "self_attn.v_proj"]))
    mx.eval(model.parameters())
    initial = [(key, mx.array(value)) for key, value in tree_flatten(model.trainable_parameters())]
    base = lambda: [(key, value) for key, value in tree_flatten(model.parameters()) if "lora_" not in key]
    initial_hash = digest(initial)
    base_hash = digest(base())
    weights = mx.load(str(args.adapter.resolve()))
    loaded_hash = digest(weights.items())
    model.update(tree_unflatten(list(weights.items())))
    mx.eval(model.parameters())

    def generate() -> str:
        prompt = tokenizer.apply_chat_template([{"role": "user", "content": "Reply with exactly READY."}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        return "".join(chunk.text for chunk in stream_generate(model, tokenizer, prompt, max_tokens=12, sampler=make_sampler(temp=0.0)))

    adapter_output = generate()
    model.update(tree_unflatten(initial))
    mx.eval(model.parameters())
    restored_output = generate()
    expected = json.loads(args.expected.read_text())
    report = {
        "status": "complete",
        "python": platform.python_version(),
        "base_hash": base_hash,
        "initial_adapter_hash": initial_hash,
        "loaded_adapter_hash": loaded_hash,
        "expected_trained_adapter_hash": expected["trained_adapter_hash"],
        "adapter_output": adapter_output,
        "restored_output": restored_output,
        "base_unchanged_after_reset": digest(base()) == base_hash,
        "adapter_hash_matches_saved": loaded_hash == expected["trained_adapter_hash"],
        "restored_generation_matches_base_probe": restored_output == "READY",
        "seconds": time.monotonic() - started,
        "peak_mlx_bytes": int(mx.get_peak_memory()),
    }
    report["passed"] = all([report["base_unchanged_after_reset"], report["adapter_hash_matches_saved"], report["restored_generation_matches_base_probe"]])
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
