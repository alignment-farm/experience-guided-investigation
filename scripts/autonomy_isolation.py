"""Observed native-tool outputs and saved/load/reset state checks."""
import json,time
from pathlib import Path
import mlx.core as mx
from mlx.utils import tree_flatten,tree_unflatten
from mlx_lm import load,stream_generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tuner.utils import linear_to_lora_layers
from train_adapter import digest
R=Path('evidence/autonomy-03');tick=time.monotonic();mx.set_memory_limit(12*1024**3);mx.set_cache_limit(256*1024**2)
m,t=load(str(Path('../weight-consolidation/models/qwen3-4b-4bit').resolve()));m.freeze();m.eval();mx.random.seed(17)
linear_to_lora_layers(m,8,dict(rank=8,scale=2.0,dropout=0.0,keys=['self_attn.q_proj','self_attn.v_proj']));mx.eval(m.parameters())
initial=[(k,mx.array(v)) for k,v in tree_flatten(m.trainable_parameters())]
base=lambda:[(k,v) for k,v in tree_flatten(m.parameters()) if 'lora_' not in k]
bh=digest(base());rows=[json.loads(x) for x in (R/'acquisition/training.jsonl').read_text().splitlines()]
prompts=[t.apply_chat_template(r['messages'],tools=r['tools'],tokenize=False,add_generation_prompt=True,enable_thinking=False) for r in [rows[0],rows[-3]]]
def generate():
 mx.random.seed(17)
 return [''.join(c.text for c in stream_generate(m,t,p,max_tokens=96,sampler=make_sampler(temp=0))) for p in prompts]
before=generate();m.update(tree_unflatten(list(mx.load(str(R/'adapter-cached-v2/adapter.safetensors')).items())));mx.eval(m.parameters());loaded=digest(tree_flatten(m.trainable_parameters()));adapted=generate()
m.update(tree_unflatten(initial));mx.eval(m.parameters());restored=generate();summary=json.loads((R/'adapter-cached-v2/summary.json').read_text())
checks={'live_loaded_hash_matches_saved':loaded==summary['trained_adapter_hash'],'base_unchanged':digest(base())==bh,'initial_adapter_restored':digest(tree_flatten(m.trainable_parameters()))==digest(initial),'observed_outputs_restored':before==restored}
report={'checks':checks,'passed':all(checks.values()),'adapter_changes_observed_output':before!=adapted,'before':before,'adapted':adapted,'restored':restored,'seconds':time.monotonic()-tick,'peak_mlx_bytes':mx.get_peak_memory(),'loaded_hash':loaded,'base_hash':bh,'boundary':'Separate fresh prompt caches; episodes additionally reset OS process. No assertion that changed output is useful learning.'}
(R/'isolation.json').write_text(json.dumps(report,indent=2));print(json.dumps(checks));assert all(checks.values())
