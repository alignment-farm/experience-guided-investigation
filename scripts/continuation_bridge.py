"""Single on-policy action-choice correction from the new adapter's own loop."""
import hashlib
import json
import shutil
from pathlib import Path
from workload import write_workspace
from continuation_runtime import Environment,render
root=Path('evidence/continuation-02');out=root/'bridge';out.mkdir(exist_ok=False)
source=root/'runs/reacquisition-correction-adapter/events.jsonl'
es=[json.loads(x) for x in source.read_text().splitlines()]
workspace=out/'workspace';write_workspace(workspace,'dev-filter-fresh',history=root/'expanded-history')
env=Environment(workspace);transcript='';prefix=[]
for turn in [0,1]:
 m=next(e for e in es if e['kind']=='model' and e['turn']==turn)
 result=env.call(m['action'])
 assert result==next(e for e in es if e['kind']=='tool' and e['turn']==turn)['result']
 transcript+='\nASSISTANT: '+m['raw']+'\nTOOL: '+json.dumps(result,sort_keys=True)
 prefix.append({'turn':turn,'raw':m['raw'],'action':m['action'],'result':result})
failed=next(e for e in es if e['kind']=='model' and e['turn']==2)
assert failed['prompt']==render((workspace/'TASK.md').read_text(),transcript)
rows=[json.loads(x) for x in (root/'correction/training.jsonl').read_text().splitlines()]
action=json.loads(rows[2]['target']);result=env.call(action)
assert result['application_ok'] and result['assertion_passed'] is False
row={'id':'bridge-read-to-probe','prompt':failed['prompt'],'target':rows[2]['target']}
(out/'training.jsonl').write_text(json.dumps(row)+'\n')
(out/'executed-target.json').write_text(json.dumps({'prefix':prefix,'replaced_action':failed['action'],'teacher_action':action,'result':result},indent=2))
(out/'lineage.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'turn':2,'initial_adapter':'correction-adapter/adapter.safetensors','intervention':'Replace actual learner read with executed mixed-type probe; one row, four updates, no other new targets.','authorship':'investigator target reuses previously executed correction probe','selection':'on-policy development loop; no fresh outcomes'},indent=2))
print('Prepared one executed on-policy bridge correction.')
