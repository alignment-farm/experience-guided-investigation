"""Native-tool LoRA with a recomputed full prefix and stopped prefix gradients."""
import argparse
import hashlib
import json
import math
import random
import time
from pathlib import Path
from train_adapter import digest

def main():
 p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--training',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--epochs',type=int,default=2);p.add_argument('--seed',type=int,default=17);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 with (a.output/'events.jsonl').open('w') as log:
  def emit(kind,**data):log.write(json.dumps(dict(kind=kind,elapsed=time.monotonic()-start,**data))+'\n');log.flush()
  try:
   import mlx.core as mx
   import mlx.nn as nn
   import mlx.optimizers as optim
   from mlx.utils import tree_flatten
   from mlx_lm import load
   from mlx_lm.tuner.utils import linear_to_lora_layers
   from mlx_lm.models.cache import make_prompt_cache
   mx.set_memory_limit(12*1024**3);mx.set_cache_limit(256*1024**2)
   model,tok=load(str(Path(a.model).resolve()));model.freeze();mx.random.seed(a.seed)
   linear_to_lora_layers(model,8,dict(rank=8,scale=2.0,dropout=0.0,keys=['self_attn.q_proj','self_attn.v_proj']));mx.eval(model.parameters())
   initial=digest(tree_flatten(model.trainable_parameters()));base=lambda:[(k,v) for k,v in tree_flatten(model.parameters()) if 'lora_' not in k];base_hash=digest(base())
   rows=[json.loads(x) for x in a.training.read_text().splitlines()];encoded=[]
   for row in rows:
    prefix=tok.apply_chat_template(row['messages'],tools=row['tools'],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    full=tok.apply_chat_template(row['messages']+[row['assistant']],tools=row['tools'],tokenize=False,add_generation_prompt=False,enable_thinking=False)
    assert full.startswith(prefix),row['id']
    prefix_ids=tok.encode(prefix,add_special_tokens=False);ids=tok.encode(full,add_special_tokens=False)
    assert ids[:len(prefix_ids)]==prefix_ids,row['id']
    assert len(ids)<=16384,(row['id'],len(ids))
    encoded.append({'id':row['id'],'ids':ids,'start':len(prefix_ids)})
   manifest={'rows':[{'id':r['id'],'input_tokens':len(r['ids']),'supervised_tokens':len(r['ids'])-r['start']} for r in encoded]}
   (a.output/'training_manifest.json').write_text(json.dumps(manifest,indent=2))
   emit('provenance',model=str(Path(a.model).resolve()),training_sha256=hashlib.sha256(a.training.read_bytes()).hexdigest(),seed=a.seed,rows=len(rows),epochs=a.epochs,learning_rate=5e-5,base_hash=base_hash,initial_adapter_hash=initial,trainable_parameters=sum(v.size for k,v in tree_flatten(model.trainable_parameters())),memory_limit_bytes=12*1024**3,output_head='supervised positions only',gradient_method='full conditioning; recomputed prefix KV with stopped gradients; suffix-only backprop; not full-SFT gradient')
   def loss_fn(m,ids,start):
    hidden=m.model(ids[:,:-1])[:,start-1:,:]
    logits=m.model.embed_tokens.as_linear(hidden) if m.args.tie_word_embeddings else m.lm_head(hidden)
    return nn.losses.cross_entropy(logits,ids[:,start:],reduction='mean')
   def full_loss(m,ids,start):return nn.losses.cross_entropy(m(ids[:,:-1])[:,start-1:,:],ids[:,start:],reduction='mean')
   def prefix_cache(ids,start):
    cache=make_prompt_cache(model)
    for offset in range(0,start-1,512):
     h=model.model(ids[:,offset:min(offset+512,start-1)],cache=cache)
     mx.eval(h,[c.state for c in cache]);del h
    for c in cache:
     keys,values,offset=c.state;c.state=(mx.stop_gradient(keys),mx.stop_gradient(values),offset)
    return cache
   def cached_loss(m,ids,start,cache):
    hidden=m.model(ids[:,start-1:-1],cache=cache)
    logits=m.model.embed_tokens.as_linear(hidden) if m.args.tie_word_embeddings else m.lm_head(hidden)
    return nn.losses.cross_entropy(logits,ids[:,start:],reduction='mean')
   equivalence=[]
   for label,ids,start in [('small',mx.array(encoded[0]['ids'][:64])[None,:],32),('full_row',mx.array(encoded[-1]['ids'])[None,:],encoded[-1]['start'])]:
    model.eval();old=loss_fn(model,ids,start);mx.eval(old);cache=prefix_cache(ids,start);new=cached_loss(model,ids,start,cache);mx.eval(new)
    check={'case':label,'full_context_loss':float(old.item()),'cached_prefix_loss':float(new.item()),'loss_abs_difference':float(mx.abs(old-new).item())}
    assert check['loss_abs_difference']<0.02,check
    equivalence.append(check);emit('forward_equivalence',**check)
    del old,new,cache;mx.clear_cache()
   assert mx.get_peak_memory()<=12*1024**3,'Forward validation exceeded memory budget'
   optimizer=optim.AdamW(learning_rate=5e-5,weight_decay=0.0);grad_fn=nn.value_and_grad(model,cached_loss);rng=random.Random(a.seed);losses=[];step=0
   for epoch in range(a.epochs):
    order=list(range(len(encoded)));rng.shuffle(order)
    for i in order:
     if time.monotonic()-start>2100:raise TimeoutError('35-minute training budget reached')
     r=encoded[i];ids=mx.array(r['ids'])[None,:];tick=time.monotonic();model.eval();cache=prefix_cache(ids,r['start']);model.train()
     loss,grad=grad_fn(model,ids,r['start'],cache);optimizer.update(model,grad);mx.eval(model.parameters(),optimizer.state,loss)
     value=float(loss.item());assert math.isfinite(value);step+=1;losses.append(value)
     emit('train_step',epoch=epoch,step=step,row=r['id'],loss=value,seconds=time.monotonic()-tick,active_mlx_bytes=int(mx.get_active_memory()),peak_mlx_bytes=int(mx.get_peak_memory()))
     assert mx.get_peak_memory()<=12*1024**3,'Measured training peak exceeded memory budget'
     del grad,ids,loss,cache;mx.clear_cache()
   learned=tree_flatten(model.trainable_parameters());trained_hash=digest(learned);assert trained_hash!=initial;assert digest(base())==base_hash
   mx.save_safetensors(str(a.output/'adapter.safetensors'),dict(learned))
   summary={'status':'complete','rows':len(rows),'epochs':a.epochs,'steps':step,'loss_first':losses[0],'loss_last':losses[-1],'base_hash':base_hash,'initial_adapter_hash':initial,'trained_adapter_hash':trained_hash,'adapter_bytes':(a.output/'adapter.safetensors').stat().st_size,'seconds':time.monotonic()-start,'peak_mlx_bytes':int(mx.get_peak_memory()),'forward_equivalence':equivalence,'gradient_method':'recomputed stopped-prefix KV; suffix-only backprop'}
   (a.output/'summary.json').write_text(json.dumps(summary,indent=2));emit('complete',**summary)
  except BaseException as exc:
   emit('failure',error=repr(exc));(a.output/'summary.json').write_text(json.dumps({'status':'failed','error':repr(exc),'seconds':time.monotonic()-start},indent=2));raise

if __name__=='__main__':main()
