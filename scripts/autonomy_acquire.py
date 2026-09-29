"""Executed development corrections and native-format learner-grounded targets."""
import copy
import hashlib
import json
import shutil
from pathlib import Path
from autonomy_tools import Environment
from workload import write_workspace
from continuation_evaluate import evaluate
root=Path('evidence/autonomy-03');out=root/'acquisition';out.mkdir(exist_ok=False)
rows=[];lineage=[]
for task in ['dev-filter-fresh','dev-normalization']:
 run=root/'runs'/(task+'-ordinary-replay');events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
 provenance=next(e for e in events if e['kind']=='provenance');messages=copy.deepcopy(provenance['initial_messages']);schemas=provenance['tool_schemas']
 work=out/task/'workspace';write_workspace(work,task,history=root/'reuse-history');env=Environment(work);records=[]
 # Exclude demonstrated bad source edits from targets; retain every real turn
 # and feedback as the context for subsequent recovery, and in full history.
 exclude_edits={4,6} if task=='dev-filter-fresh' else {5}
 for model in [e for e in events if e['kind']=='model']:
  turn=model['turn'];action=model['action']
  if action and action['action']=='done':break
  tool=next(e for e in events if e['kind']=='tool' and e['turn']==turn)
  actual=env.call(action) if action else tool['result']
  def stable(x):return {k:v for k,v in x.items() if k!='seconds'}
  assert stable(actual)==stable(tool['result']),(task,turn,actual,tool['result'])
  before=model['raw'].split('<tool_call>',1)[0].strip()
  target={'role':'assistant','content':before,'tool_calls':[{'type':'function','function':{'name':action['action'],'arguments':{k:v for k,v in action.items() if k!='action'}}}]}
  eligible=turn not in exclude_edits and (tool['result'].get('ok') or action['action'] in ['probe','replay'])
  if eligible:rows.append({'id':task+'-learner-'+str(turn),'messages':copy.deepcopy(messages),'assistant':target,'tools':schemas,'origin':'learner generated','source_event':str(run/'events.jsonl'),'turn':turn})
  records.append({'origin':'learner generated','turn':turn,'action':action,'result':tool['result'],'supervised':eligible})
  messages.extend([target,{'role':'tool','name':action['action'],'content':json.dumps(tool['result'],sort_keys=True)}])
 if task=='dev-filter-fresh':
  corrections=[{'action':'test'},{'action':'done','message':'Current mixed-type filter probe and retained filter check passed; the six current public regression tests also passed.'}]
 else:
  invalid={'action':'probe','steps':[{'op':'rename','from':3,'to':'a'}],'rows':[],'error_code':'SCHEMA_VALIDATION_FAILED','error_path':'pipeline.steps[0].from'}
  corrections=[invalid,{'action':'edit','old':'    source = step["from"].strip()\n    target = step["to"].strip()','new':'    source = clean_text(step["from"], path + ".from", "rename.from")\n    target = clean_text(step["to"], path + ".to", "rename.to")'},invalid,{'action':'replay','case_id':'rename_trim'},{'action':'test'},{'action':'done','message':'Current trimmed rename succeeds, invalid source type returns the schema error at pipeline.steps[0].from, and all six public regression tests pass.'}]
 for i,action in enumerate(corrections):
  target={'role':'assistant','content':'','tool_calls':[{'type':'function','function':{'name':action['action'],'arguments':{k:v for k,v in action.items() if k!='action'}}}]}
  rows.append({'id':task+'-teacher-'+str(i),'messages':copy.deepcopy(messages),'assistant':target,'tools':schemas,'origin':'investigator correction','source_event':str(run/'events.jsonl'),'turn':'replacement continuation'})
  result=env.call(action);records.append({'origin':'investigator correction','action':action,'result':result,'supervised':True})
  messages.extend([target,{'role':'tool','name':action['action'],'content':json.dumps(result,sort_keys=True)}])
 report=evaluate(work);assert report['complete'],report
 (out/task/'events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in records));(out/task/'messages.json').write_text(json.dumps(messages,indent=2));(out/task/'evaluation.json').write_text(json.dumps(report,indent=2))
 lineage.append({'task':task,'source_sha256':hashlib.sha256((run/'events.jsonl').read_bytes()).hexdigest(),'masked_source_edit_turns':sorted(exclude_edits),'teacher_actions':len(corrections),'interpretation':'Corrections based on actual development attempts; external development type failure informs rename diagnosis. No future material used. Past original clean_text implementation supports guard repair; no new examiner implementation exposed.'})
(out/'training.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));(out/'lineage.json').write_text(json.dumps(lineage,indent=2))
print('Native supervised rows:',len(rows),'learner:',sum(x['origin']=='learner generated' for x in rows),'teacher:',sum(x['origin']=='investigator correction' for x in rows))
