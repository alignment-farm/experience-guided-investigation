"""Mechanical action/cost audit; interpretation remains in the report."""
import json,hashlib
from pathlib import Path
R=Path('evidence/autonomy-03');reports={}
for run in sorted((R/'runs').iterdir()):
 p=run/'events.jsonl'
 if not p.exists():continue
 events=[json.loads(x) for x in p.read_text().splitlines()];models=[e for e in events if e['kind']=='model'];tool=[e for e in events if e['kind']=='tool'];summary=json.loads((run/'summary.json').read_text()) if (run/'summary.json').exists() else None
 reports[run.name]={'summary':summary,'interrupted':(run/'intervention.json').exists(),'elapsed_seconds':events[-1].get('elapsed'),'model_turns':len(models),'malformed_calls':sum(not e.get('action') for e in models),'actions':[{'turn':e['turn'],'action':e['action'],'ok':e['result'].get('ok'),'assertion_passed':e['result'].get('assertion_passed')} for e in tool],'public_test_calls':sum(bool(e['action']) and e['action'].get('action')=='test' for e in tool),'failed_assertions':sum(e['result'].get('assertion_passed') is False for e in tool),'passed_assertions':sum(e['result'].get('assertion_passed') is True for e in tool),'local_prompt_tokens':sum(e.get('prompt_tokens',0) for e in models),'local_completion_tokens':sum(e.get('completion_tokens',0) for e in models),'events_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(R/'action-audit.json').write_text(json.dumps(reports,indent=2));print('Audited',len(reports),'episodes; completion is not inferred from done.')
