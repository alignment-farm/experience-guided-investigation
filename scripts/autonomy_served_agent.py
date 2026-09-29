"""Bounded ordinary reference through the user-provided Docker Model Runner API."""
import argparse
import json
import time
import urllib.request
from pathlib import Path
from autonomy_tools import Environment,initial_messages,TOOLS
from workload import source_hash
ENDPOINT='https://mac-studio-7hr7.taile71f88.ts.net/engines/v1/chat/completions'
MODEL='docker.io/ai/qwen3.8:27b-q4_K_M'

def main():
 p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--max-turns',type=int,default=16);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();messages=initial_messages(a.workspace);env=Environment(a.workspace)
 with (a.output/'events.jsonl').open('w') as log:
  def emit(kind,**data):log.write(json.dumps(dict(kind=kind,elapsed=time.monotonic()-start,**data))+'\n');log.flush()
  emit('provenance',endpoint=ENDPOINT,requested_model=MODEL,initial_source_hash=source_hash(a.workspace),initial_messages=messages,tool_schemas=TOOLS,temperature=0.7,top_p=0.8,seed=17,reset='new client conversation and workspace; each request contains only this episode messages; server caches may remain')
  done=False
  try:
   for turn in range(a.max_turns):
    body={'model':MODEL,'messages':messages,'tools':TOOLS,'tool_choice':'auto','parallel_tool_calls':False,'max_tokens':1024,'temperature':0.7,'top_p':0.8,'seed':17,'stream':False}
    req=urllib.request.Request(ENDPOINT,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','User-Agent':'experience-guided-investigation/0.3 (bounded ordinary reuse reference)'})
    tick=time.monotonic()
    with urllib.request.urlopen(req,timeout=180) as response:result=json.load(response)
    message=result['choices'][0]['message'];calls=message.get('tool_calls') or []
    action=None;call=None
    if calls:
     call=calls[0];arguments=call['function']['arguments']
     try:
      args=json.loads(arguments) if isinstance(arguments,str) else arguments
      if isinstance(args,dict):action={'action':call['function']['name'],**args}
     except ValueError:pass
    emit('model',turn=turn,response=result,action=action,prompt_tokens=result.get('usage',{}).get('prompt_tokens'),completion_tokens=result.get('usage',{}).get('completion_tokens'),seconds=time.monotonic()-tick,discarded_additional_calls=len(calls)-1 if calls else 0)
    tool=env.call(action) if action else {'ok':False,'error':'No valid function call executed. Use a provided function; do not claim unperformed work.'}
    emit('tool',turn=turn,action=action,result=tool)
    if call:
     messages.extend([{'role':'assistant','content':message.get('content') or '', 'tool_calls':[call]},{'role':'tool','tool_call_id':call['id'],'content':json.dumps(tool,sort_keys=True)}])
    else:messages.extend([{'role':'assistant','content':message.get('content') or ''},{'role':'user','content':tool['error']}])
    if action and action.get('action')=='done' and tool.get('done'):done=True;break
   (a.output/'submitted.py').write_bytes((a.workspace/'etl_pipeline.py').read_bytes());(a.output/'messages.json').write_text(json.dumps(messages,indent=2))
   summary={'status':'declared_done' if done else 'turn_limit','turns':turn+1,'tool_calls':env.calls,'seconds':time.monotonic()-start,'source_hash':source_hash(a.workspace)}
   (a.output/'summary.json').write_text(json.dumps(summary,indent=2));emit('complete',**summary)
  except BaseException as exc:emit('failure',error=repr(exc));raise

if __name__=='__main__':main()
