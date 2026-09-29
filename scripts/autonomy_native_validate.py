"""Native-call boundaries and ordinary reuse assertions without a model."""
import hashlib,json,tempfile
from pathlib import Path
from autonomy_tools import Environment,first_tool
from workload import write_workspace
R=Path('evidence/autonomy-03');checks={}
first=first_tool('<tool_call>{"name":"read","arguments":{"path":"etl_pipeline.py"}}</tool_call><tool_call>{"name":"done","arguments":{"message":"x"}}</tool_call>')
checks['first_call_only']=first[0]['action']=='read'
checks['incomplete_not_executed']=first_tool('<tool_call>{"name":"edit","arguments":') is None
with tempfile.TemporaryDirectory() as d:
 for task,case in [('dev-filter-fresh','filter_boolean_only'),('dev-normalization','rename_trim'),('dev-execution','limit_zero')]:
  w=Path(d)/task;write_workspace(w,task,history=R/'reuse-history');env=Environment(w)
  before=env.call({'action':'replay','case_id':case});checks[case+'_fails_before']=before['assertion_passed'] is False
  history=w/'history/teacher-repaired.py';digest=hashlib.sha256(history.read_bytes()).hexdigest()
  result=env.call({'action':'restore','source':'history/teacher-repaired.py'});checks[case+'_restore']=result['ok']
  checks[case+'_passes_after']=env.call({'action':'replay','case_id':case})['assertion_passed'] is True
  checks[case+'_history_unchanged']=hashlib.sha256(history.read_bytes()).hexdigest()==digest
  checks[case+'_escape_rejected']=env.call({'action':'restore','source':'../etl_pipeline.py'})['ok'] is False
report={'checks':checks,'passed':all(checks.values())};(R/'final-native-validation.json').write_text(json.dumps(report,indent=2));print(report);assert report['passed']
