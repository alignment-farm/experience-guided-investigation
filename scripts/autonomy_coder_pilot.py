import subprocess
import sys
from pathlib import Path
root=Path('evidence/autonomy-03')
for task in ['dev-filter-fresh','dev-normalization']:
 name=task+'-coder-base';print('START',name,flush=True)
 subprocess.run([sys.executable,'scripts/autonomy_agent.py','--model','../weight-consolidation/models/qwen2.5-coder-7b-4bit','--workspace',str(root/'workspaces'/name),'--output',str(root/'runs'/name),'--max-turns','12'],check=True,timeout=900)
 print('END',name,flush=True)
subprocess.run([sys.executable,'scripts/continuation_evaluate.py','--root',str(root)],check=True)
