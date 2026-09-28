"""Authored subsequent change, frozen before participant evaluation."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from workload import write_workspace,BASE_SOURCE
from continuation_evaluate import evaluate

ROOT=Path('evidence/continuation-02')
REQUIREMENT='''Add the unfamiliar reject operation to the ETL CLI. Its step contains op="reject" and where, a nonempty expression string. Normalize whitespace in op and where and discard unknown fields as for filter. During execution, reject removes a row ONLY when the expression evaluates to boolean true. Every other value, including truthy nonbooleans and missing/null values, keeps the row. Preserve input order and all existing filter, map, select, rename, limit, validation and error behavior. Expression errors from reject must report pipeline.steps[i].where. Use source/history and a discriminating executable probe before declaring completion. This is a local authored extension, not an official benchmark checkpoint.'''

def fresh_cases():
 values=[True,False,1,0,-3,2.25,'keep','',None,[],{}]
 rows=[{'id':f'r{i}','flag':v} for i,v in enumerate(values)]+[{'id':'missing'}]
 return [
  {'name':'reject_mixed_types','steps':[{'op':'reject','where':'flag'}],'rows':rows,'expected':rows[1:]},
  {'name':'reject_comparison','steps':[{'op':'reject','where':'score > 4'}],'rows':[{'score':2},{'score':7},{'score':4}],'expected':[{'score':2},{'score':4}]},
  {'name':'reject_then_map_limit','steps':[{'op':'reject','where':'flag'},{'op':'map','as':'copy','expr':'id'},{'op':'limit','n':2}],'rows':rows,'expected':[dict(rows[1],copy='r1'),dict(rows[2],copy='r2')]},
  {'name':'filter_then_reject','steps':[{'op':'filter','where':'flag'},{'op':'reject','where':'flag'}],'rows':rows,'expected':[]},
  {'name':'reject_empty','steps':[{'op':'reject','where':'flag'}],'rows':[],'expected':[]},
  {'name':'reject_error','steps':[{'op':'limit','n':1},{'op':'reject','where':'fn()'}],'rows':[{}],'error':'BAD_EXPR','path':'pipeline.steps[1].where'},
  {'name':'reject_invalid_expression_type','steps':[{'op':'reject','where':7}],'rows':[],'error':'SCHEMA_VALIDATION_FAILED','path':'pipeline.steps[0].where'},
  {'name':'reject_blank','steps':[{'op':'reject','where':'  '}],'rows':[],'error':'SCHEMA_VALIDATION_FAILED','path':'pipeline.steps[0].where'},
  {'name':'reject_normalization','steps':[{'op':' REJECT ','where':' flag ','discard':'x'}],'rows':[],'normalize':[{'op':'reject','where':'flag'}]},
 ]

def grade(workspace):
 reports=[]
 for case in fresh_cases():
  cmd=[sys.executable,str(workspace/'etl_pipeline.py')]+([] if 'normalize' in case else ['--execute'])
  payload={'pipeline':{'steps':case['steps']},'dataset':case['rows']}
  run=subprocess.run(cmd,input=json.dumps(payload),text=True,capture_output=True,timeout=10)
  try: actual=json.loads(run.stdout)
  except ValueError: actual=None
  if 'error' in case:
   passed=run.returncode==1 and actual and actual.get('error_code')==case['error'] and actual.get('path')==case['path']
  else:
   expected={'status':'ok','normalized':{'steps':case['normalize']}} if 'normalize' in case else {'status':'ok','data':case['expected'],'metrics':{'rows_in':len(case['rows']),'rows_out':len(case['expected'])}}
   passed=run.returncode==0 and actual==expected
  reports.append(dict(case=case,passed=bool(passed),actual=actual,returncode=run.returncode,stderr=run.stderr))
 preserved=evaluate(workspace)
 return {'new_cases':reports,'new_passed':sum(r['passed'] for r in reports),'new_total':len(reports),'preserved':preserved,'complete':all(r['passed'] for r in reports) and preserved['complete']}

def prepare():
 examiner=ROOT/'fresh-examiner';examiner.mkdir(exist_ok=False)
 (examiner/'requirement.txt').write_text(REQUIREMENT)
 (examiner/'cases.json').write_text(json.dumps(fresh_cases(),indent=2))
 reference=examiner/'reference';write_workspace(reference,'transfer-branch')
 source=BASE_SOURCE.replace('"rename", "limit"}', '"rename", "limit", "reject"}')
 source=source.replace('if op == "filter":','if op in {"filter", "reject"}:')
 source=source.replace('elif op == "filter":','elif op in {"filter", "reject"}:')
 source=source.replace('rows = [row for row in rows if isinstance(_eval_expr(step["where"], row), bool) and _eval_expr(step["where"], row)]', 'rows = [row for row in rows if (_eval_expr(step["where"], row) is True) == (op == "filter")]')
 (reference/'etl_pipeline.py').write_text(source)
 report=grade(reference);assert report['complete'],report
 (examiner/'reference-evaluation.json').write_text(json.dumps(report,indent=2))
 for arm in ['ordinary-history','correction-adapter']:
  workspace=ROOT/'workspaces'/('fresh-reject-'+arm)
  write_workspace(workspace,'transfer-branch',history=ROOT/'expanded-history')
  (workspace/'TASK.md').write_text(REQUIREMENT)
 manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [examiner/'requirement.txt',examiner/'cases.json',ROOT/'correction-adapter/adapter.safetensors',Path('scripts/continuation_agent.py'),Path('scripts/continuation_runtime.py'),Path('scripts/continuation_fresh.py')]}
 (ROOT/'fresh-freeze.json').write_text(json.dumps({'claim':'Bounded near-transfer of strict predicate investigation after filter correction; no independent-history or official benchmark claim.','selection':'One fixed 28-update adapter; no selection on fresh outcomes.','initial_workspace':'Common correct checkpoint-2 source, all eligible earlier attempts/correction history, original public tests; both arms byte matched.','hashes':manifest},indent=2))
 print('Fresh reject change frozen; authored reference passes 9 new + 18 preserved checks and public suite.')

def score():
 report={arm:grade(ROOT/'workspaces'/('fresh-reject-'+arm)) for arm in ['ordinary-history','correction-adapter']}
 (ROOT/'fresh-evaluation.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:{x:v[x] for x in ['new_passed','new_total','complete']} for k,v in report.items()},indent=2))

if __name__=='__main__':
 prepare() if '--prepare' in sys.argv else score()
