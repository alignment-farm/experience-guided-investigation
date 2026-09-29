import json
import tempfile
from pathlib import Path
from autonomy_runtime import Environment,parse,first_action
from workload import write_workspace
checks={}
checks['first_action_never_last_done']=first_action('{"action":"read","path":"etl_pipeline.py"}{"action":"done"}')[0]['action']=='read'
checks['incomplete_does_not_execute']=first_action('{"action":"edit","old":') is None
checks['reject_composite']=parse('{"action":"edit"}{"action":"done"}') is None
checks['single_fenced_object']=parse('```json\n{"action":"test"}\n```')=={'action':'test'}
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp);write_workspace(root,'dev-filter-fresh');env=Environment(root)
 p={'action':'probe','steps':[{'op':'filter','where':'flag'}],'rows':[{'flag':True},{'flag':1},{'flag':False}],'expect':[{'flag':True}]}
 before=env.call(p);checks['bug_probe_fails']=before['application_ok'] and not before['assertion_passed']
 env.call({'action':'edit','old':'_eval_expr(step["where"], row) is not None','new':'_eval_expr(step["where"], row) is True'})
 after=env.call(p);checks['fixed_probe_passes']=after['assertion_passed']
 error=env.call({'action':'probe','steps':[{'op':'filter','where':'fn()'}],'rows':[{}],'error_code':'BAD_EXPR','error_path':'pipeline.steps[0].where'})
 checks['expected_error_passes']=error['assertion_passed'] and not error['application_ok']
 checks['wrong_wrapper_rejected']=not env.call(dict(p,expect={'data':[{'flag':True}]}))['assertion_passed']
 checks['escape_rejected']=env.call({'action':'read','path':'../outside'})['ok'] is False
 checks['read_is_copyable']='170:' not in env.call({'action':'read','path':'etl_pipeline.py'})['content']
report={'checks':checks,'passed':all(checks.values()),'before':before,'after':after,'expected_error':error}
Path('evidence/autonomy-03/harness-validation.json').write_text(json.dumps(report,indent=2));assert report['passed'];print(checks)
