import hashlib
import json
import shutil
from pathlib import Path
from workload import write_workspace
root=Path('evidence/continuation-02');history=root/'bridge-history'
shutil.copytree(root/'expanded-history',history)
for name in ['reacquisition-ordinary-history','reacquisition-correction-adapter','conditional-ordinary-history','conditional-correction-adapter']:
 run=root/'runs'/name
 assert (run/'summary.json').exists()
 events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
 content='Eligible development attempt: '+name+'\n'
 for e in events:
  if e['kind']=='injected_prefix':content+='DECLARED INJECTED PREFIX:\n'+json.dumps(e,indent=2)+'\n'
  if e['kind']=='model':
   if e['turn']==0:content+='INITIAL PROMPT:\n'+e['prompt']+'\n'
   content+='ASSISTANT:\n'+e['raw']+'\n'
  if e['kind']=='tool':content+='TOOL:\n'+json.dumps(e['result'],indent=2)+'\n'
 (history/(name+'.txt')).write_text(content)
 shutil.copy2(run/'submitted.py',history/(name+'-submitted.py'))
for name in ['training.jsonl','executed-target.json','lineage.json']:
 shutil.copy2(root/'bridge'/name,history/('bridge-'+name))
for arm in ['ordinary-history','bridge-adapter']:
 write_workspace(root/'workspaces'/('bridge-'+arm),'dev-filter-fresh',history=history)
(root/'bridge-history-manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(history.iterdir())},indent=2))
