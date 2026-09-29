"""Prepare byte-matched ordinary development controls without running them."""
import argparse,hashlib,json
from pathlib import Path
from workload import write_workspace
R=Path('evidence/autonomy-03');p=argparse.ArgumentParser();p.add_argument('--name',default='joint-acquisition-ordinary4');a=p.parse_args();W=R/'workspaces'/a.name;assert not W.exists();write_workspace(W,'dev-filter-fresh',history=R/'complete-history')
s=(W/'etl_pipeline.py').read_text().replace('source = clean_text(step["from"], path + ".from", "rename.from")','source = step["from"].strip()').replace('target = clean_text(step["to"], path + ".to", "rename.to")','target = step["to"].strip()');(W/'etl_pipeline.py').write_text(s)
f=json.loads((R/'joint-freeze.json').read_text());(W/'TASK.md').write_text(f['task']);assert hashlib.sha256(s.encode()).hexdigest()==f['source_sha256'];assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'history').iterdir()}==f['history']
print('Byte-matched initial joint control prepared:',a.name)
