"""Compare observed base outputs before and after actual adapter load/reset."""
import argparse
import gc
import json
import time
from pathlib import Path
import mlx.core as mx
from mlx.utils import tree_flatten,tree_unflatten
from mlx_lm import load,stream_generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tuner.utils import linear_to_lora_layers
from train_adapter import digest
p=argparse.ArgumentParser();p.add_argument('--adapter-dir',default='correction-adapter');p.add_argument('--output',default='isolation.json');args=p.parse_args()
root=Path('evidence/continuation-02');started=time.monotonic()
model,tok=load(str(Path('../weight-consolidation/models/qwen3-4b-4bit').resolve()))
model.freeze();mx.random.seed(17)
linear_to_lora_layers(model,8,dict(rank=8,scale=2.0,dropout=0.0,keys=['self_attn.q_proj','self_attn.v_proj']))
mx.eval(model.parameters())
initial=[(k,mx.array(v)) for k,v in tree_flatten(model.trainable_parameters())]
base=lambda:[(k,v) for k,v in tree_flatten(model.parameters()) if 'lora_' not in k]
base_hash=digest(base())
rows=[json.loads(x) for x in (root/'correction/training.jsonl').read_text().splitlines()]
prompts=['Reply with exactly READY.',rows[0]['prompt'],rows[2]['prompt']]
def outputs():
 out=[]
 for p in prompts:
  rendered=tok.apply_chat_template([{'role':'user','content':p}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
  out.append(''.join(c.text for c in stream_generate(model,tok,rendered,max_tokens=192,sampler=make_sampler(temp=0.0))))
 return out
before=outputs()
weights=mx.load(str(root/args.adapter_dir/'adapter.safetensors'))
model.update(tree_unflatten(list(weights.items())));mx.eval(model.parameters())
live_hash=digest(tree_flatten(model.trainable_parameters()))
adapted=outputs()
model.update(tree_unflatten(initial));mx.eval(model.parameters())
restored=outputs()
expected=json.loads((root/args.adapter_dir/'summary.json').read_text())
checks={'live_loaded_hash_matches_saved':live_hash==expected['trained_adapter_hash'],'base_unchanged':digest(base())==base_hash,'restored_state_hash_matches_initial':digest(tree_flatten(model.trainable_parameters()))==digest(initial),'observed_generations_restored':before==restored,'adapter_changes_at_least_one_output':before!=adapted}
report={'checks':checks,'passed':all(checks.values()),'base_outputs':before,'adapted_outputs':adapted,'restored_outputs':restored,'loaded_hash':live_hash,'base_hash':base_hash,'seconds':time.monotonic()-started,'peak_mlx_bytes':int(mx.get_peak_memory()),'boundary':'Each generation uses a fresh prompt cache; explicit adapter reset checked against actual observed base outputs, not a presumed READY answer. Maintenance episodes additionally use separate OS processes.'}
(root/args.output).write_text(json.dumps(report,indent=2));print(json.dumps(checks,indent=2));assert all(checks.values())
