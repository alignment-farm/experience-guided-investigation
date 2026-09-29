"""Conditional frozen fresh extension; never run preparation before acquisition decision."""
import argparse,hashlib,json,shutil
from pathlib import Path
from workload import write_workspace
from continuation_fresh import REQUIREMENT,grade
R=Path('evidence/autonomy-03')
p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');a=p.parse_args()
names=['ordinary4','learned4','ordinary27']
if a.prepare:
 decision=json.loads((R/'joint-evaluation.json').read_text())
 assert decision['mechanical_gate_passed'], 'Fresh transfer withheld: autonomous acquisition gate failed.'
 H=R/'fresh-history';shutil.copytree(R/'complete-history',H)
 for name in ['events.jsonl','messages.json','submitted.py','summary.json']:
  src=R/'runs/joint-acquisition-learned'/name
  if src.exists():shutil.copy2(src,H/('joint-acquisition-'+name))
 (H/'INDEX.md').write_text('The joint-acquisition-* files record the subsequent learned development attempt in full; they are equally accessible to all arms.\n'+(H/'INDEX.md').read_text())
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in H.iterdir() if p.is_file()}
 for name in names:
  W=R/'workspaces'/('fresh-reject-'+name);write_workspace(W,'transfer-branch',history=H);(W/'TASK.md').write_text(REQUIREMENT)
  assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'history').iterdir()}==hashes
 files=[R/'adapter-cached-v2/adapter.safetensors',Path('scripts/autonomy_tool_agent.py'),Path('scripts/autonomy_served_agent.py'),Path('scripts/autonomy_tools.py'),Path('scripts/autonomy_runtime.py'),Path('scripts/continuation_fresh.py')]
 (R/'fresh-freeze.json').write_text(json.dumps({'history':hashes,'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'requirement':REQUIREMENT,'arms':names,'selection':'Fixed 46-update adapter. Fresh extension unobserved before freeze; no treatment selection on fresh outcomes.','parity':'Byte-identical initial code, tests, task and complete eligible history. 27B separate competence reference.'},indent=2))
 print('Frozen three fresh arms.')
else:
 reports={n:grade(R/'workspaces'/('fresh-reject-'+n)) for n in names}
 (R/'fresh-evaluation.json').write_text(json.dumps(reports,indent=2));print(json.dumps({k:{x:v[x] for x in ['new_passed','new_total','complete']} for k,v in reports.items()}))
