"""Conditional diagnostic: inject and replay the three recorded learner prefix turns."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from continuation_runtime import Environment, render, parse
from workload import source_hash


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True)
    p.add_argument('--adapter')
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-turns', type=int, default=12)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    with (a.output/'events.jsonl').open('w') as log:
        def emit(kind, **data):
            log.write(json.dumps(dict(kind=kind, elapsed=time.monotonic()-started, **data))+'\n'); log.flush()
        try:
            import mlx.core as mx
            from mlx_lm import load, stream_generate
            from mlx_lm.sample_utils import make_sampler
            model, tok = load(str(Path(a.model).resolve()))
            model.freeze()
            if a.adapter:
                from mlx.utils import tree_unflatten
                from mlx_lm.tuner.utils import linear_to_lora_layers
                linear_to_lora_layers(model, 8, dict(rank=8,scale=2.0,dropout=0.0,keys=['self_attn.q_proj','self_attn.v_proj']))
                weights = mx.load(a.adapter)
                model.update(tree_unflatten(list(weights.items())))
                mx.eval(model.parameters())
            emit('provenance', model=str(Path(a.model).resolve()), adapter_sha256=hashlib.sha256(Path(a.adapter).read_bytes()).hexdigest() if a.adapter else None,
                 initial_source_hash=source_hash(a.workspace), max_tokens=1024, temperature=0, reset='fresh process; no supplied prompt/KV cache')
            env = Environment(a.workspace)
            transcript = ''
            prefix_events = [json.loads(x) for x in Path('evidence/continuation-02/correction/events.jsonl').read_text().splitlines()][:3]
            for e in prefix_events:
                actual = env.call(e['action']) if e['action'] else {'ok':False,'error':'Expected exactly one complete JSON action; nothing executed.'}
                assert actual == e['result']
                transcript += '\nASSISTANT: '+e['raw']+'\nTOOL: '+json.dumps(actual,sort_keys=True)
                emit('injected_prefix', **e)

            done = False
            for turn in range(a.max_turns):
                prompt = render((a.workspace/'TASK.md').read_text(), transcript)
                rendered = tok.apply_chat_template([{'role':'user','content':prompt}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
                tick = time.monotonic()
                chunks = list(stream_generate(model, tok, rendered, max_tokens=1024, sampler=make_sampler(temp=0.0)))
                raw = ''.join(c.text for c in chunks)
                action = parse(raw)
                emit('model', turn=turn, prompt=prompt, raw=raw, action=action, prompt_tokens=len(tok.encode(rendered)), completion_tokens=chunks[-1].generation_tokens if chunks else 0, seconds=time.monotonic()-tick)
                result = env.call(action) if action else {'ok':False,'error':'Expected exactly one complete JSON action; nothing executed.'}
                emit('tool', turn=turn, action=action, result=result)
                transcript += '\nASSISTANT: '+raw+'\nTOOL: '+json.dumps(result,sort_keys=True)
                if action and action.get('action') == 'done' and result.get('done'):
                    done = True
                    break
            (a.output/'submitted.py').write_bytes((a.workspace/'etl_pipeline.py').read_bytes())
            summary = dict(status='declared_done' if done else 'turn_limit', turns=turn+1, tool_calls=env.calls, seconds=time.monotonic()-started, peak_mlx_bytes=int(mx.get_peak_memory()), source_hash=source_hash(a.workspace))
            (a.output/'summary.json').write_text(json.dumps(summary,indent=2)); emit('complete', **summary)
        except BaseException as exc:
            emit('failure',error=repr(exc)); raise

if __name__ == '__main__':
    main()
