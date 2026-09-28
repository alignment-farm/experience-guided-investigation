"""Make all eligible attempts and corrections equally recoverable in both arms."""
import hashlib
import json
import shutil
from pathlib import Path
from workload import write_workspace
root=Path('evidence/continuation-02')
history=root/'expanded-history'
shutil.copytree(root/'eligible-history',history)
for run in sorted((root/'runs').iterdir()):
 if not (run/'summary.json').exists(): continue
 events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
 content='Eligible participant development attempt: '+run.name+'\n'
 for e in events:
  if e['kind']=='model':
   if e['turn']==0: content+='INITIAL PROMPT:\n'+e['prompt']+'\n'
   content+='ASSISTANT:\n'+e['raw']+'\n'
  if e['kind']=='tool': content+='TOOL:\n'+json.dumps(e['result'],indent=2)+'\n'
 (history/(run.name+'.txt')).write_text(content)
 shutil.copy2(run/'submitted.py',history/(run.name+'-submitted.py'))
 shutil.copy2(root/'workspaces'/run.name/'tests/test_public.py',history/(run.name+'-public.py'))
for name in ['transcript.txt','events.jsonl','lineage.json','training.jsonl']:
 if name.endswith('.jsonl'):
  rows=[json.loads(x) for x in (root/'correction'/name).read_text().splitlines()]
  (history/('teacher-'+name+'.txt')).write_text('\n'.join(json.dumps(x,indent=2) for x in rows))
 else: shutil.copy2(root/'correction'/name,history/('teacher-'+name))
shutil.copy2(root/'correction/workspace/etl_pipeline.py',history/'teacher-repaired.py')
# External examiner results are NOT in participant history.
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(history.iterdir())}
(root/'history-manifest.json').write_text(json.dumps(manifest,indent=2))
for arm in ['ordinary-history','correction-adapter']:
 write_workspace(root/'workspaces'/('reacquisition-'+arm),'dev-filter-fresh',history=history)
print('Equal full source history prepared:',len(manifest),'files')
