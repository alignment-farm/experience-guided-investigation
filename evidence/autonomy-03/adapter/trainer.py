"""Native-tool LoRA with a target-position output head and checkpointed layers."""
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
   from mlx_lm.tuner.trainer import grad_checkpoint
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
   emit('provenance',model=str(Path(a.model).resolve()),training_sha256=hashlib.sha256(a.training.read_bytes()).hexdigest(),seed=a.seed,rows=len(rows),epochs=a.epochs,learning_rate=5e-5,base_hash=base_hash,initial_adapter_hash=initial,trainable_parameters=sum(v.size for k,v in tree_flatten(model.trainable_parameters())),memory_limit_bytes=12*1024**3,output_head='supervised positions only; equivalent objective checked below')
   def loss_fn(m,ids,start):
    hidden=m.model(ids[:,:-1])[:,start-1:,:]
    logits=m.model.embed_tokens.as_linear(hidden) if m.args.tie_word_embeddings else m.lm_head(hidden)
    return nn.losses.cross_entropy(logits,ids[:,start:],reduction='mean')
   def full_loss(m,ids,start):return nn.losses.cross_entropy(m(ids[:,:-1])[:,start-1:,:],ids[:,start:],reduction='mean')
   sample=mx.array(encoded[0]['ids'][:64])[None,:]
   old,old_grad=nn.value_and_grad(model,full_loss)(model,sample,32)
   new,new_grad=nn.value_and_grad(model,loss_fn)(model,sample,32)
   mx.eval(old,new,old_grad,new_grad)
   old_items=dict(tree_flatten(old_grad));new_items=dict(tree_flatten(new_grad))
   grad_diff=max(float(mx.max(mx.abs(old_items[k]-new_items[k])).item()) for k in old_items)
   equivalence={'full_loss':float(old.item()),'target_head_loss':float(new.item()),'loss_abs_difference':float(mx.abs(old-new).item()),'max_gradient_abs_difference':grad_diff}
   assert equivalence['loss_abs_difference']<0.01 and grad_diff<0.01,equivalence
   emit('loss_equivalence',**equivalence)
   del old_grad,new_grad,old_items,new_items,old,new,sample
   mx.clear_cache();grad_checkpoint(model.layers[0])
   optimizer=optim.AdamW(learning_rate=5e-5,weight_decay=0.0);grad_fn=nn.value_and_grad(model,loss_fn);rng=random.Random(a.seed);losses=[];step=0
   for epoch in range(a.epochs):
    order=list(range(len(encoded)));rng.shuffle(order)
    for i in order:
     if time.monotonic()-start>2100:raise TimeoutError('35-minute training budget reached')
     r=encoded[i];ids=mx.array(r['ids'])[None,:];model.train();tick=time.monotonic()
     loss,grad=grad_fn(model,ids,r['start']);optimizer.update(model,grad);mx.eval(model.parameters(),optimizer.state,loss)
     value=float(loss.item());assert math.isfinite(value);step+=1;losses.append(value)
     emit('train_step',epoch=epoch,step=step,row=r['id'],loss=value,seconds=time.monotonic()-tick,active_mlx_bytes=int(mx.get_active_memory()),peak_mlx_bytes=int(mx.get_peak_memory()))
     del grad,ids,loss;mx.clear_cache()
   learned=tree_flatten(model.trainable_parameters());trained_hash=digest(learned);assert trained_hash!=initial;assert digest(base())==base_hash
   mx.save_safetensors(str(a.output/'adapter.safetensors'),dict(learned))
   summary={'status':'complete','rows':len(rows),'epochs':a.epochs,'steps':step,'loss_first':losses[0],'loss_last':losses[-1],'base_hash':base_hash,'initial_adapter_hash':initial,'trained_adapter_hash':trained_hash,'adapter_bytes':(a.output/'adapter.safetensors').stat().st_size,'seconds':time.monotonic()-start,'peak_mlx_bytes':int(mx.get_peak_memory()),'loss_equivalence':equivalence}
   (a.output/'summary.json').write_text(json.dumps(summary,indent=2));emit('complete',**summary)
  except BaseException as exc:
   emit('failure',error=repr(exc));(a.output/'summary.json').write_text(json.dumps({'status':'failed','error':repr(exc),'seconds':time.monotonic()-start},indent=2));raise

if __name__=='__main__':main()
