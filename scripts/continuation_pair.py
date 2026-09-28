import argparse
import subprocess
import sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prefix',default='reacquisition');a=p.parse_args()
root=Path('evidence/continuation-02')
for arm in ['ordinary-history','correction-adapter']:
 name=a.prefix+'-'+arm
 command=[sys.executable,'scripts/continuation_agent.py','--model','../weight-consolidation/models/qwen3-4b-4bit','--workspace',str(root/'workspaces'/name),'--output',str(root/'runs'/name)]
 if arm=='correction-adapter': command+=['--adapter',str(root/'correction-adapter/adapter.safetensors')]
 print('START',name,flush=True)
 subprocess.run(command,check=True,timeout=900)
 print('END',name,flush=True)
subprocess.run([sys.executable,'scripts/continuation_evaluate.py'],check=True)
