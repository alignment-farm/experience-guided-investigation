import subprocess
import sys
import time
from pathlib import Path
root=Path('evidence/continuation-02')
start=time.monotonic()
for task in ['dev-filter-fresh','dev-normalization','dev-execution']:
    for arm in ['base','pilot-adapter']:
        if time.monotonic()-start>5400:
            raise SystemExit('90 minute budget exhausted')
        name=task+'-'+arm
        command=[sys.executable,'scripts/continuation_agent.py','--model','../weight-consolidation/models/qwen3-4b-4bit','--workspace',str(root/'workspaces'/name),'--output',str(root/'runs'/name)]
        if arm=='pilot-adapter':
            command+=['--adapter','evidence/pilot-01/adapter-retry-01/adapter.safetensors']
        print('START',name,flush=True)
        result=subprocess.run(command,timeout=max(1,5400-(time.monotonic()-start)))
        print('END',name,result.returncode,flush=True)
        if result.returncode: raise SystemExit(result.returncode)
subprocess.run([sys.executable,'scripts/continuation_evaluate.py'],check=True)
