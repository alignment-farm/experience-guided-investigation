import subprocess
import sys
from pathlib import Path
root=Path('evidence/autonomy-03')
for task in ['dev-filter-fresh','dev-normalization']:
 name=task+'-ordinary-served27';print('START',name,flush=True)
 subprocess.run([sys.executable,'scripts/autonomy_served_agent.py','--workspace',str(root/'workspaces'/name),'--output',str(root/'runs'/name)],check=True,timeout=1200)
 print('END',name,flush=True)
subprocess.run([sys.executable,'scripts/continuation_evaluate.py','--root',str(root)],check=True)
