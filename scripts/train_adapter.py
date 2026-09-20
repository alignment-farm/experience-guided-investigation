"""Train the fixed pilot LoRA from executed investigation trajectories."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import platform
import random
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
    parser.add_argument("--training", type=Path, required=True, help="JSONL rows with prompt and target")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    events = (args.output / "events.jsonl").open("w")

    def emit(kind: str, **data):
        events.write(json.dumps({"kind": kind, "elapsed": time.monotonic() - started, **data}) + "\n")
        events.flush()

    try:
        import mlx.core as mx
        import mlx.nn as nn
        import mlx.optimizers as optim
        from mlx.utils import tree_flatten, tree_unflatten
        from mlx_lm import load
        from mlx_lm.tuner.utils import linear_to_lora_layers

        rows = [json.loads(line) for line in args.training.read_text().splitlines() if line.strip()]
        if not rows:
            raise ValueError("empty training set")
        model_dir = args.model.resolve()
        model, tokenizer = load(str(model_dir))
        model.freeze()
        linear_to_lora_layers(model, 8, dict(rank=8, scale=2.0, dropout=0.0, keys=["self_attn.q_proj", "self_attn.v_proj"]))
        mx.eval(model.parameters())
        initial = [(key, mx.array(value)) for key, value in tree_flatten(model.trainable_parameters())]
        base_items = lambda: [(key, value) for key, value in tree_flatten(model.parameters()) if "lora_" not in key]
        base_hash = digest(base_items())
        initial_hash = digest(initial)
        emit(
            "provenance",
            python=platform.python_version(),
            packages={name: md.version(name) for name in ["mlx", "mlx-lm", "transformers"]},
            model=str(model_dir),
            rows=len(rows),
            epochs=args.epochs,
            seed=args.seed,
            base_hash=base_hash,
            initial_adapter_hash=initial_hash,
            trainable_parameters=sum(value.size for _, value in initial),
        )

        encoded = []
        for row in rows:
            content = row["prompt"]
            target = row["target"]
            rendered = tokenizer.apply_chat_template([{"role": "user", "content": content}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
            prefix = tokenizer.encode(rendered)
            full = tokenizer.encode(rendered + target) + [tokenizer.eos_token_id]
            if full[: len(prefix)] != prefix:
                raise AssertionError("target boundary is not token stable")
            encoded.append({"ids": full, "start": len(prefix), "id": row.get("id", str(len(encoded)))})
        (args.output / "training_manifest.json").write_text(json.dumps({"rows": [{"id": r["id"], "input_tokens": len(r["ids"]), "supervised_tokens": len(r["ids"]) - r["start"]} for r in encoded]}, indent=2))
        emit("prepared", input_tokens=sum(len(r["ids"]) for r in encoded), supervised_tokens=sum(len(r["ids"]) - r["start"] for r in encoded))

        def loss_fn(m, ids, start):
            outputs = m(ids[:, :-1])
            return nn.losses.cross_entropy(outputs[:, start - 1 :, :], ids[:, start:], reduction="mean")

        grad_fn = nn.value_and_grad(model, loss_fn)
        optimizer = optim.AdamW(learning_rate=0.0003, weight_decay=0.0)
        rng = random.Random(args.seed)
        step = 0
        losses = []
        for epoch in range(args.epochs):
            order = list(range(len(encoded)))
            rng.shuffle(order)
            for row_index in order:
                row = encoded[row_index]
                ids = mx.array(row["ids"])[None, :]
                model.train()
                tick = time.monotonic()
                loss, grads = grad_fn(model, ids, row["start"])
                optimizer.update(model, grads)
                mx.eval(model.parameters(), optimizer.state, loss)
                value = float(loss.item())
                if not value == value:
                    raise FloatingPointError("non-finite loss")
                step += 1
                losses.append(value)
                emit("train_step", epoch=epoch, row=row["id"], step=step, loss=value, seconds=time.monotonic() - tick)

        trained = [(key, mx.array(value)) for key, value in tree_flatten(model.trainable_parameters())]
        trained_hash = digest(trained)
        if trained_hash == initial_hash:
            raise AssertionError("adapter did not change")
        mx.save_safetensors(str(args.output / "adapter.safetensors"), dict(trained))
        if digest(base_items()) != base_hash:
            raise AssertionError("base parameters changed during LoRA training")
        summary = {
            "status": "complete",
            "steps": step,
            "epochs": args.epochs,
            "rows": len(rows),
            "loss_first": losses[0],
            "loss_last": losses[-1],
            "base_hash": base_hash,
            "initial_adapter_hash": initial_hash,
            "trained_adapter_hash": trained_hash,
            "adapter_bytes": (args.output / "adapter.safetensors").stat().st_size,
            "seconds": time.monotonic() - started,
            "peak_mlx_bytes": int(mx.get_peak_memory()),
        }
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
