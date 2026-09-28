import subprocess
import sys
from pathlib import Path
root=Path('evidence/continuation-02')
if '--prepare' in sys.argv:
 from workload import write_workspace
 for arm in ['ordinary-history','correction-adapter']:
  write_workspace(root/'workspaces'/('conditional-'+arm),'dev-filter-fresh',history=root/'expanded-history')
 raise SystemExit(0)
for arm in ['ordinary-history','correction-adapter']:
 name='conditional-'+arm
 command=[sys.executable,'scripts/continuation_resume_agent.py','--model','../weight-consolidation/models/qwen3-4b-4bit','--workspace',str(root/'workspaces'/name),'--output',str(root/'runs'/name)]
 if arm=='correction-adapter':command+=['--adapter',str(root/'correction-adapter/adapter.safetensors')]
 print('START',name,flush=True);subprocess.run(command,check=True,timeout=900);print('END',name,flush=True)
subprocess.run([sys.executable,'scripts/continuation_evaluate.py'],check=True)
subprocess.run([sys.executable,'scripts/continuation_isolation.py'],check=True)
