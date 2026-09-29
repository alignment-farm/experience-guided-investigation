"""One fresh native-conversation maintenance episode."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from autonomy_tools import Environment,initial_messages,first_tool,TOOLS
from workload import source_hash


def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--adapter');p.add_argument('--workspace',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--max-turns',type=int,default=20);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    with (a.output/'events.jsonl').open('w') as log:
        def emit(kind,**data):log.write(json.dumps(dict(kind=kind,elapsed=time.monotonic()-started,**data))+'\n');log.flush()
        try:
            import mlx.core as mx
            from mlx_lm import load,stream_generate
            from mlx_lm.sample_utils import make_sampler
            model,tok=load(str(Path(a.model).resolve()));model.freeze();model.eval();mx.random.seed(17)
            if a.adapter:
                from mlx.utils import tree_unflatten
                from mlx_lm.tuner.utils import linear_to_lora_layers
                linear_to_lora_layers(model,8,dict(rank=8,scale=2.0,dropout=0.0,keys=['self_attn.q_proj','self_attn.v_proj']))
                model.update(tree_unflatten(list(mx.load(a.adapter).items())));mx.eval(model.parameters());model.eval()
            mx.random.seed(17)  # Reset after optional LoRA initialization for matched inference RNG.
            messages=initial_messages(a.workspace);env=Environment(a.workspace)
            emit('provenance',model=str(Path(a.model).resolve()),adapter_sha256=hashlib.sha256(Path(a.adapter).read_bytes()).hexdigest() if a.adapter else None,initial_source_hash=source_hash(a.workspace),initial_messages=messages,tool_schemas=TOOLS,max_tokens=1024,temperature=0.7,top_p=0.8,top_k=20,seed=17,reset='new OS process, new model load and conversation; no supplied KV cache')
            done=False
            for turn in range(a.max_turns):
                rendered=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False,tools=TOOLS)
                tick=time.monotonic();chunks=[];raw='';boundary=None
                generator=stream_generate(model,tok,rendered,max_tokens=1024,sampler=make_sampler(temp=0.7,top_p=0.8,top_k=20))
                for chunk in generator:
                    chunks.append(chunk);raw+=chunk.text
                    boundary=first_tool(raw)
                    if boundary:break
                generator.close()
                action=boundary[0] if boundary else None
                executed_text=('<tool_call>\n'+json.dumps(boundary[2])+'\n</tool_call>') if boundary else raw
                emit('model',turn=turn,raw=raw,executed_text=executed_text,first_object_stop=boundary is not None,action=action,prompt_tokens=len(tok.encode(rendered)),completion_tokens=chunks[-1].generation_tokens if chunks else 0,seconds=time.monotonic()-tick)
                result=env.call(action) if action else {'ok':False,'error':'Expected exactly one JSON object; no action executed. Correct the JSON syntax or issue a simpler action.'}
                emit('tool',turn=turn,action=action,result=result)
                if boundary:
                    messages.extend([{'role':'assistant','content':boundary[1],'tool_calls':[{'type':'function','function':boundary[2]}]},{'role':'tool','name':boundary[2]['name'],'content':json.dumps(result,sort_keys=True)}])
                else:
                    messages.extend([{'role':'assistant','content':raw},{'role':'user','content':'No function was executed. Use a provided function call and wait for its result.'}])
                if action and action.get('action')=='done' and result.get('done'):done=True;break
            (a.output/'submitted.py').write_bytes((a.workspace/'etl_pipeline.py').read_bytes())
            (a.output/'messages.json').write_text(json.dumps(messages,indent=2))
            summary=dict(status='declared_done' if done else 'turn_limit',turns=turn+1,tool_calls=env.calls,seconds=time.monotonic()-started,peak_mlx_bytes=int(mx.get_peak_memory()),source_hash=source_hash(a.workspace))
            (a.output/'summary.json').write_text(json.dumps(summary,indent=2));emit('complete',**summary)
        except BaseException as exc:emit('failure',error=repr(exc));raise

if __name__=='__main__':main()
