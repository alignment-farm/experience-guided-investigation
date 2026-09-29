"""Separate program correctness from actual current-workspace procedure evidence."""
import argparse,json
from pathlib import Path
from continuation_evaluate import evaluate
from autonomy_confirmation import grade
p=argparse.ArgumentParser();p.add_argument('--name',default='joint-acquisition-learned');a=p.parse_args();R=Path('evidence/autonomy-03');name=a.name;work=R/'workspaces'/name;run=R/'runs'/name
es=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()];ts=[e for e in es if e['kind']=='tool'];report={'development':evaluate(work),'confirmation':grade(work)}
last_edit=max([e['turn'] for e in ts if e['action'] and e['action']['action'] in ['edit','restore'] and e['result'].get('ok')] or [-1])
valid=[e for e in ts if e['result'].get('assertion_passed') is True]
def is_filter(e):
 a=e['action']
 if a.get('case_id')=='filter_boolean_only':return True
 rows=a.get('rows',[]);steps=a.get('steps',[])
 return any(x.get('op')=='filter' for x in steps) and any(any(v is True for v in r.values()) for r in rows) and any(any((isinstance(v,str) and bool(v)) or (type(v) in [int,float] and bool(v)) for v in r.values()) for r in rows)
def is_rename_error(e):
 a=e['action'];return a.get('error_code')=='SCHEMA_VALIDATION_FAILED' and any(x.get('op')=='rename' and any(k in x and not isinstance(x[k],str) for k in ['from','to']) for x in a.get('steps',[]))
checks={'submitted_development_complete':report['development']['complete'],'fresh_contract_confirmation_complete':report['confirmation']['complete'],'current_public_suite_executed':any(e['turn']>last_edit and e['action'] and e['action']['action']=='test' and e['result'].get('ok') for e in ts),'current_mixed_type_filter_verified':any(is_filter(e) for e in valid),'current_invalid_type_rename_verified':any(is_rename_error(e) for e in valid),'declared_done':any(e['action'] and e['action']['action']=='done' for e in ts)}
report.update(checks=checks,mechanical_gate_passed=all(checks.values()),last_successful_source_change=last_edit,failed_assertions=[e['turn'] for e in ts if e['result'].get('assertion_passed') is False],note='Procedure predicates are audit aids; inspect exact probe/expectation and done content before a scientific claim. Inspect whether later edits invalidate earlier passed assertions; still-valid checks need not be repeated. Public suite must follow final source change. No post-outcome teacher intervention.')
(R/('joint-evaluation.json' if name=='joint-acquisition-learned' else name+'-evaluation.json')).write_text(json.dumps(report,indent=2));print(json.dumps(checks,indent=2))
