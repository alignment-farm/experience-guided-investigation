"""Disclosed native costs; elapsed work is not isolated GPU occupancy or repayment."""
import json
from pathlib import Path
R=Path('evidence/autonomy-03');episodes=[];training=[]
for p in sorted((R/'runs').glob('*/events.jsonl')):
 events=[json.loads(x) for x in p.read_text().splitlines()]
 if not events:continue
 models=[e for e in events if e['kind']=='model']
 episodes.append({'name':p.parent.name,'elapsed_seconds':events[-1].get('elapsed'),'prompt_tokens':sum(e.get('prompt_tokens') or 0 for e in models),'generated_tokens':sum(e.get('completion_tokens') or 0 for e in models),'server_reported_cached_prompt_tokens':sum(e.get('response',{}).get('usage',{}).get('prompt_tokens_details',{}).get('cached_tokens',0) for e in models),'model_calls':len(models),'interrupted':(p.parent/'intervention.json').exists(),'complete_record':events[-1]['kind'] in ['complete','failure'],'token_boundary':'Local generation tokens or server-reported usage; server usage may include reasoning. Not directly comparable across models.'})
for name in ['adapter','adapter-cached','adapter-cached-v2']:
 root=R/name;p=root/'events.jsonl'
 if not p.exists():continue
 es=[json.loads(x) for x in p.read_text().splitlines()];steps=[e for e in es if e['kind']=='train_step'];valid_time=name!='adapter-cached'
 training.append({'name':name,'recorded_updates':len(steps),'elapsed_seconds':es[-1].get('elapsed') if valid_time else None,'time_invalid_reason':None if valid_time else 'Token-position variable overwrote timing start; use no logged duration for cost. Conservative budget charge60 seconds.','budget_seconds':es[-1].get('elapsed') if valid_time else 60,'peak_mlx_bytes':max([e.get('peak_mlx_bytes',0) for e in es] or [0]),'losses':[{'row':e['row'],'epoch':e['epoch'],'loss':e['loss']} for e in steps]})
isolation=json.loads((R/'isolation.json').read_text()) if (R/'isolation.json').exists() else {}
report={'episodes':episodes,'training_attempts':training,'recorded_updates':sum(x['recorded_updates'] for x in training),'episode_elapsed_seconds':sum(x['elapsed_seconds'] or 0 for x in episodes),'training_budget_seconds':sum(x['budget_seconds'] or 0 for x in training),'isolation_seconds':isolation.get('seconds',0),'paid_participant_api_calls':0,'investigator_teacher_costs':'Unknown; eight executed correction actions and their raw traces disclosed, plus development diagnosis and shared interface implementation.','interpretation':'Elapsed costs include loading, tool execution and shared-machine contention; not exclusive device occupancy. No repayment claim. One interrupted full-gradient step may have begun additional uncommitted evaluation before termination.'}
report['conservative_serial_heavy_seconds']=report['episode_elapsed_seconds']+report['training_budget_seconds']+report['isolation_seconds']
(R/'costs.json').write_text(json.dumps(report,indent=2));print({k:report[k] for k in ['recorded_updates','conservative_serial_heavy_seconds','episode_elapsed_seconds']})
