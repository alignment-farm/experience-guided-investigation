"""Index executable checks already present in eligible source experience."""
import hashlib
import json
import shutil
from pathlib import Path
from workload import write_workspace
root=Path('evidence/autonomy-03');history=root/'reuse-history';shutil.copytree(root/'history',history)
cases={}
# The expectations come from recorded successful executions of the original
# authored teaching repairs, not a newly queried examiner or new future task.
for task,label in [('dev-normalization','rename_trim'),('dev-execution','limit_zero')]:
 source=Path('evidence/pilot-01/acquisition')/task/'events.jsonl'
 for e in map(json.loads,source.read_text().splitlines()):
  action=e['action']
  if action['action']!='probe':continue
  actual=json.loads(e['result']['stdout']);assert actual['status']=='ok'
  payload=action['payload']
  cases[label]={'action':{'action':'probe','steps':payload['pipeline']['steps'],'rows':payload['dataset'],'expect':actual['data']},'expectation_origin':'recorded actual output of original executed teacher repair','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_turn':e['turn'],'full_record_in_workspace':'history/'+task+'.txt'}
source=Path('evidence/continuation-02/correction/events.jsonl')
for e in map(json.loads,source.read_text().splitlines()):
 a=e['action'] or {}
 if a.get('action')=='probe' and 'expected' in a:
  payload=a['payload'];cases['filter_boolean_only']={'action':{'action':'probe','steps':payload['pipeline']['steps'],'rows':payload['dataset'],'expect':a['expected']['data']},'expectation_origin':'explicit expected result in the executed investigator correction; failed before strict edit and passed after','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_turn':e['turn'],'full_record_in_workspace':'history/teacher-events.jsonl.txt'}
  break
# Keep all newer attempts (including failures) accessible without adding their
# incorrect expectations to these three declared reusable teacher checks.
for run in sorted((root/'runs').iterdir()):
 p=run/'events.jsonl'
 if p.exists():shutil.copy2(p,history/(run.name+'-events.jsonl'))
 if (run/'submitted.py').exists():shutil.copy2(run/'submitted.py',history/(run.name+'-submitted.py'))
(history/'CASES.json').write_text(json.dumps(cases,indent=2))
index=(history/'INDEX.md').read_text()+'\nEXECUTABLE PAST CHECKS (replay by case_id; raw provenance in history/CASES.json):\n'
for name,c in cases.items():index+='- '+name+': '+json.dumps(c['action'],separators=(',',':'))+'\n'
index+='Replaying executes the recorded check against CURRENT code. For a new requirement, adapt or construct your own probe; these old checks alone may be insufficient.\n'
(history/'INDEX.md').write_text(index)
(root/'reuse-history-manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(history.iterdir())},indent=2))
for task in ['dev-filter-fresh','dev-normalization']:
 write_workspace(root/'workspaces'/(task+'-ordinary-replay'),task,history=history)
print('Three existing teacher checks indexed for ordinary executable reuse; no new cases authored.')
