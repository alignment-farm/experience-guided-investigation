"""Behavioral controls for scoring and action boundaries, no model inference."""
import json
import tempfile
from pathlib import Path
from continuation_runtime import Environment,parse
from continuation_evaluate import evaluate
from workload import write_workspace

checks={}
checks['composite_rejected']=parse('{"action":"edit"}\n{"action":"done"}') is None
checks['truncated_rejected']=parse('{"action":"edit","new":"') is None
checks['single_accepted']=parse('{"action":"test"}')=={'action':'test'}
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)
 write_workspace(root,'dev-filter-fresh')
 env=Environment(root)
 checks['escape_rejected']=env.call({'action':'read','path':'../secret'})['ok'] is False
 page=env.call({'action':'read','path':'etl_pipeline.py','start':100,'limit':100})
 checks['pagination']=page['next_start']==200 and page['total_lines']==229
 bad=env.call({'action':'probe','payload':{'steps':[],'dataset':[]}})
 checks['schema_error_explicit']=bad['ok'] is False and bad['application_ok'] is False
 initial=evaluate(root)
 path=root/'etl_pipeline.py'
 source=path.read_text()
 path.write_text(source.replace('_eval_expr(step["where"], row) is not None','_eval_expr(step["where"], row)'))
 truthy=evaluate(root)
 path.write_text(source.replace('_eval_expr(step["where"], row) is not None','_eval_expr(step["where"], row) is True'))
 correct=evaluate(root)
 checks['initial_rejected']=initial['complete'] is False
 checks['truthy_rejected']=truthy['complete'] is False
 checks['strict_accepted']=correct['complete'] is True
report={'checks':checks,'passed':all(checks.values()),'negative_control_scores':{'unrepaired':initial['passed'],'truthy':truthy['passed'],'strict':correct['passed']}}
Path('evidence/continuation-02/harness-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report['passed']
