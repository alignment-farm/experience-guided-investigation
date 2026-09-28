"""Executed investigator corrections rooted in a saved participant failure."""
import hashlib
import json
from pathlib import Path
from continuation_runtime import Environment,render
from continuation_evaluate import evaluate
from workload import write_workspace

root=Path('evidence/continuation-02')
out=root/'correction';out.mkdir(exist_ok=False)
workspace=out/'workspace'
write_workspace(workspace,'dev-filter-fresh',history=root/'eligible-history')
env=Environment(workspace)
source=root/'runs/dev-filter-fresh-pilot-adapter/events.jsonl'
events=[json.loads(x) for x in source.read_text().splitlines()]
transcript=''
replayed=[]
# Preserve the learner prefix exactly, including the rejected malformed action.
for turn in range(3):
 model=next(e for e in events if e['kind']=='model' and e['turn']==turn)
 tool=next(e for e in events if e['kind']=='tool' and e['turn']==turn)
 actual=env.call(model['action']) if model['action'] else {'ok':False,'error':'Expected exactly one complete JSON action; nothing executed.'}
 assert actual==tool['result'],(actual,tool['result'])
 transcript+='\nASSISTANT: '+model['raw']+'\nTOOL: '+json.dumps(actual,sort_keys=True)
 replayed.append({'turn':turn,'raw':model['raw'],'action':model['action'],'result':actual})
rows=[{'id':0,'flag':True},{'id':1,'flag':1},{'id':2,'flag':'yes'},{'id':3,'flag':False},{'id':4,'flag':None},{'id':5}]
payload={'pipeline':{'steps':[{'op':'filter','where':'flag'}]},'dataset':rows}
expected={'status':'ok','data':[rows[0]],'metrics':{'rows_in':6,'rows_out':1}}
actions=[
 {'action':'probe','payload':payload,'expected':expected},
 {'action':'edit','path':'etl_pipeline.py','old':'rows = [row for row in rows if _eval_expr(step["where"], row) is not None]','new':'rows = [row for row in rows if _eval_expr(step["where"], row) is True]'},
 {'action':'probe','payload':payload,'expected':expected},
 {'action':'test'},
 {'action':'done','message':'The mixed boolean/nonboolean probe now retains only true; all six preserved visible tests pass.'}
]
training=[];teacher=[]
for turn in [0,1]:
 model=next(e for e in events if e['kind']=='model' and e['turn']==turn)
 training.append({'id':f'learner-prefix-{turn}','prompt':model['prompt'],'target':model['raw']})
for i,action in enumerate(actions):
 prompt=render((workspace/'TASK.md').read_text(),transcript)
 target=json.dumps(action,separators=(',',':'))
 result=env.call(action)
 training.append({'id':f'correction-{i}','prompt':prompt,'target':target})
 teacher.append({'turn':3+i,'action':action,'result':result,'authorship':'investigator correction; not learner generated'})
 transcript+='\nASSISTANT: '+target+'\nTOOL: '+json.dumps(result,sort_keys=True)
assert teacher[0]['result']['assertion_passed'] is False
assert teacher[2]['result']['assertion_passed'] is True
assert teacher[3]['result']['ok'] is True
report=evaluate(workspace)
assert report['complete']
(out/'training.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in training))
(out/'events.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in replayed+teacher))
(out/'transcript.txt').write_text(transcript)
(out/'evaluation.json').write_text(json.dumps(report,indent=2))
(out/'lineage.json').write_text(json.dumps({'source_events':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'preserved_turns':[0,1,2],'replaced_turn':3,'teacher_actions':len(actions),'training_rows':len(training),'learner_authored_targets':2,'teacher_authored_targets':5,'intervention':'Replace premature truthy repair with discriminating probe, strict repair and executed verification. Five-turn authored continuation after exact learner prefix; NOT a replication of single-turn-only correction.','training_initialization':'base Qwen3, not prior adapter; prefix came from pilot-adapter policy, disclosed cross-policy correction','selection':'development failure inspection; no confirmation outcomes used'},indent=2))
print('Teacher correction passes 18/18 external checks and six public tests; seven training rows (two learner actions and five corrections).')
