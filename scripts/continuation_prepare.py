import json
from pathlib import Path
from workload import write_workspace

ROOT = Path('evidence/continuation-02')

def main():
    history = ROOT/'eligible-history'
    history.mkdir(exist_ok=True)
    for task in ['dev-normalization','dev-execution']:
        old = Path('evidence/pilot-01/acquisition')/task
        (history/(task+'.txt')).write_text('Researcher-authored pilot teaching, not participant experience.\n'+(old/'transcript.txt').read_text())
    rows = [json.loads(x) for x in Path('evidence/pilot-01/acquisition/training.jsonl').read_text().splitlines()]
    for i,row in enumerate(rows):
        (history/f'training-{i:02d}.txt').write_text('Exact eligible pilot training row.\nPROMPT:\n'+row['prompt']+'\nTARGET:\n'+row['target'])
    for task in ['dev-normalization','dev-execution','dev-filter-fresh']:
        for arm in ['base','pilot-adapter']:
            workspace = ROOT/'workspaces'/f'{task}-{arm}'
            if workspace.exists():
                raise FileExistsError(workspace)
            write_workspace(workspace,task,history=history)
    print('Prepared six isolated development workspaces with identical full eligible history.')

if __name__ == '__main__': main()
