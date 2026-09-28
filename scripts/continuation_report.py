"""Summarize frozen submissions, behavior, matched artifacts and native costs."""
import hashlib
import json
from pathlib import Path
root=Path('evidence/continuation-02')
evaluations=json.loads((root/'evaluation.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
runs={}
for d in sorted((root/'runs').iterdir()):
 if not (d/'summary.json').exists():continue
 events=[json.loads(x) for x in (d/'events.jsonl').read_text().splitlines()]
 models=[e for e in events if e['kind']=='model'];tools=[e for e in events if e['kind']=='tool']
 provenance=next(e for e in events if e['kind']=='provenance')
 history=root/'workspaces'/d.name/'history'
 runs[d.name]={'summary':json.loads((d/'summary.json').read_text()),'evaluation':{k:evaluations[d.name][k] for k in ['passed','total','complete']},'public_passed':evaluations[d.name]['public']['returncode']==0,
  'prompt_tokens':sum(e['prompt_tokens'] for e in models),'completion_tokens':sum(e['completion_tokens'] for e in models),'model_seconds':sum(e['seconds'] for e in models),'invalid_actions':sum(e['action'] is None for e in models),'cap_hits':sum(e['completion_tokens']>=1024 for e in models),
  'successful_edits':sum((e['action'] or {}).get('action')=='edit' and e['result'].get('ok',False) for e in tools),
  'successful_probes':sum((e['action'] or {}).get('action')=='probe' and e['result'].get('application_ok',False) for e in tools),
  'passed_probe_assertions':sum(e['result'].get('assertion_passed',False) for e in tools),
  'failed_probe_assertions':sum(e['result'].get('assertion_passed') is False for e in tools),
  'history_searches':sum((e['action'] or {}).get('action')=='history_search' for e in tools),
  'history_reads':sum((e['action'] or {}).get('action')=='read' and str((e['action'] or {}).get('path','')).startswith('history/') for e in tools),
  'injected_prefix_turns':sum(e['kind']=='injected_prefix' for e in events),
  'initial_source_hash':provenance['initial_source_hash'],'submitted_sha256':sha(d/'submitted.py'),
  'submission_matches_evaluated_workspace':sha(d/'submitted.py')==sha(root/'workspaces'/d.name/'etl_pipeline.py'),
  'history_manifest':{p.name:sha(p) for p in sorted(history.iterdir())}}
paired=[]
for prefix,arms in [('dev-normalization',['base','pilot-adapter']),('dev-execution',['base','pilot-adapter']),('dev-filter-fresh',['base','pilot-adapter']),('reacquisition',['ordinary-history','correction-adapter']),('conditional',['ordinary-history','correction-adapter']),('bridge',['ordinary-history','bridge-adapter'])]:
 names=[prefix+'-'+a for a in arms]
 if not all(n in runs for n in names):continue
 a,b=[runs[n] for n in names]
 paired.append({'names':names,'initial_source_equal':a['initial_source_hash']==b['initial_source_hash'],'full_history_equal':a['history_manifest']==b['history_manifest'],'task_equal':sha(root/'workspaces'/names[0]/'TASK.md')==sha(root/'workspaces'/names[1]/'TASK.md'),'public_tests_equal':sha(root/'workspaces'/names[0]/'tests/test_public.py')==sha(root/'workspaces'/names[1]/'tests/test_public.py')})
training=json.loads((root/'correction-adapter/summary.json').read_text())
bridge=json.loads((root/'bridge-adapter/summary.json').read_text())
costs={'episodes':len(runs),'model_calls':sum(v['summary']['turns'] for v in runs.values()),'prompt_tokens':sum(v['prompt_tokens'] for v in runs.values()),'completion_tokens':sum(v['completion_tokens'] for v in runs.values()),'episode_wall_seconds':sum(v['summary']['seconds'] for v in runs.values()),'model_generation_seconds':sum(v['model_seconds'] for v in runs.values()),'training_wall_seconds':training['seconds']+bridge['seconds'],'training_updates':training['steps']+bridge['steps'],'training_peak_mlx_bytes':training['peak_mlx_bytes'],'training_rows':training['rows']+bridge['rows'],'teacher_authored_actions':6,'distinct_teacher_action_json':4,'learner_authored_training_actions':2,'investigator_and_teacher_tokens':'unknown','investigator_and_teacher_monetary_cost':'unknown','external_validation_wall_time':'not comprehensively instrumented','prior_pilot_cost':'excluded from new-run totals; preserved in pilot-01','new_paid_participant_api_calls':0}
if (root/'isolation.json').exists():costs['isolation_seconds']=json.loads((root/'isolation.json').read_text())['seconds']
if (root/'bridge-isolation.json').exists():costs['bridge_isolation_seconds']=json.loads((root/'bridge-isolation.json').read_text())['seconds']
report={'starting_revision':'121242ca597c607f06d9f9084d88b1fa90a458ff','runs':runs,'paired_state_checks':paired,'costs':costs,'fresh_confirmation':'prepared and frozen but not executed; no fresh-transfer claim','interpretation_boundary':'All executed maintenance cases are development, including coached conditional-prefix runs. Behavioral completion uses bounded external checks plus public suite; target procedure is separately audited.'}
(root/'analysis.json').write_text(json.dumps(report,indent=2))
assert all(v['submission_matches_evaluated_workspace'] for v in runs.values())
assert all(all(p[k] for k in ['initial_source_equal','full_history_equal','task_equal','public_tests_equal']) for p in paired)
print(json.dumps(costs,indent=2))
