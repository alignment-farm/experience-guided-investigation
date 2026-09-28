import subprocess
import sys
from pathlib import Path
root=Path('evidence/continuation-02')
for arm in ['ordinary-history','bridge-adapter']:
 name='bridge-'+arm
 command=[sys.executable,'scripts/continuation_agent.py','--model','../weight-consolidation/models/qwen3-4b-4bit','--workspace',str(root/'workspaces'/name),'--output',str(root/'runs'/name)]
 if arm=='bridge-adapter':command+=['--adapter',str(root/'bridge-adapter/adapter.safetensors')]
 print('START',name,flush=True);subprocess.run(command,check=True,timeout=900);print('END',name,flush=True)
subprocess.run([sys.executable,'scripts/continuation_evaluate.py'],check=True)

subprocess.run([sys.executable,'scripts/continuation_isolation.py','--adapter-dir','bridge-adapter','--output','bridge-isolation.json'],check=True)
