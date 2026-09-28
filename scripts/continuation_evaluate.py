"""External development checks: never delivered as episode feedback."""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def evaluate(root):
    cases=[]
    def check(name,steps,rows,expected=None,error=None,path=None):
        payload={'pipeline':{'steps':steps},'dataset':rows}
        run=subprocess.run([sys.executable,str(root/'etl_pipeline.py'),'--execute'],input=json.dumps(payload),text=True,capture_output=True,timeout=10)
        try: actual=json.loads(run.stdout)
        except ValueError: actual=None
        if error:
            passed=run.returncode==1 and actual and actual.get('error_code')==error and actual.get('path')==path
        else:
            passed=run.returncode==0 and actual=={'status':'ok','data':expected,'metrics':{'rows_in':len(rows),'rows_out':len(expected)}}
        cases.append(dict(name=name,payload=payload,expected_data=expected,expected_error=error,expected_path=path,actual=actual,passed=bool(passed),returncode=run.returncode,stderr=run.stderr))
    values=[True,False,1,0,-2,1.5,'yes','',None]
    rows=[{'id':i,'flag':v} for i,v in enumerate(values)]+[{'id':9}]
    check('filter_boolean_only',[{'op':'filter','where':'flag'}],rows,[rows[0]])
    for i,v in enumerate(values):
        check(f'filter_type_{i}',[{'op':'filter','where':'flag'}],[{'flag':v}],[{'flag':v}] if v is True else [])
    check('filter_comparison',[{'op':'filter','where':'age > 30'}],[{'age':25},{'age':35}],[{'age':35}])
    check('filter_error',[{'op':'filter','where':'fn()'}],[{'id':1}],error='BAD_EXPR',path='pipeline.steps[0].where')
    check('rename_trim',[{'op':'rename','from':' amount ','to':' price '}],[{'amount':3}],[{'price':3}])
    check('rename_invalid',[{'op':'rename','from':3,'to':'a'}],[],error='SCHEMA_VALIDATION_FAILED',path='pipeline.steps[0].from')
    check('limit_zero',[{'op':'limit','n':0}],[{'id':1}],[])
    check('limit_positive',[{'op':'limit','n':1}],[{'id':1},{'id':2}],[{'id':1}])
    for name,n in [('boolean',True),('negative',-1)]:
        check('limit_'+name,[{'op':'limit','n':n}],[],error='SCHEMA_VALIDATION_FAILED',path='pipeline.steps[0].n')
    suite=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=root,text=True,capture_output=True,timeout=30)
    return dict(cases=cases,passed=sum(c['passed'] for c in cases),total=len(cases),public=dict(returncode=suite.returncode,stdout=suite.stdout,stderr=suite.stderr),complete=all(c['passed'] for c in cases) and suite.returncode==0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('evidence/continuation-02'));a=p.parse_args()
    report={w.name:evaluate(w) for w in sorted((a.root/'workspaces').iterdir()) if (a.root/'runs'/w.name/'summary.json').exists()}
    (a.root/'evaluation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:{x:v[x] for x in ['passed','total','complete']} for k,v in report.items()},indent=2))
