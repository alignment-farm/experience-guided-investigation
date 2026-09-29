"""Freeze complete eligible history and a combined, already-exposed acquisition task."""
import hashlib,json,shutil
from pathlib import Path
from workload import write_workspace
R=Path('evidence/autonomy-03');H=R/'complete-history'
shutil.copytree(R/'reuse-history',H)
for run in sorted((R/'runs').iterdir()):
 for name in ['events.jsonl','messages.json','submitted.py','summary.json','intervention.json']:
  p=run/name
  if p.exists():shutil.copy2(p,H/(run.name+'-'+name))
for task in ['dev-filter-fresh','dev-normalization']:
 for name in ['events.jsonl','messages.json']:
  shutil.copy2(R/'acquisition'/task/name,H/('correction-'+task+'-'+name))
 shutil.copy2(R/'acquisition'/task/'workspace/etl_pipeline.py',H/('correction-'+task+'-repaired.py'))
shutil.copy2(R/'acquisition/training.jsonl',H/'native-training.jsonl')
shutil.copy2(R/'acquisition/lineage.json',H/'native-training-lineage.json')
index=(H/'INDEX.md').read_text()
(H/'INDEX.md').write_text('''Latest eligible development corrections:
- correction-dev-filter-fresh-repaired.py and correction-dev-normalization-repaired.py: complete reusable corrected programs, including boolean-only filter and clean_text rename validation.
- correction-dev-filter-fresh-events.jsonl: actual failed probes and repairs, followed by current public regression verification.
- correction-dev-normalization-events.jsonl: trim repair, invalid from=3 probe failure, clean_text correction, repeated schema-error probe, retained trim check, and public suite.
- native-training.jsonl and native-training-lineage.json: all supervised targets, with origin and masking disclosure.
- All recent failed and successful ordinary attempts remain here in full. No future requirements or examiner code included.

'''+index)
work=R/'workspaces/joint-acquisition-learned';write_workspace(work,'dev-filter-fresh',history=H)
s=(work/'etl_pipeline.py').read_text();s=s.replace('source = clean_text(step["from"], path + ".from", "rename.from")','source = step["from"].strip()').replace('target = clean_text(step["to"], path + ".to", "rename.to")','target = step["to"].strip()');(work/'etl_pipeline.py').write_text(s)
(work/'TASK.md').write_text('''Repair both current regressions: filter must retain a row only for boolean true, and rename must trim field names while preserving existing schema validation and error paths for invalid field-name types. Preserve every earlier operation. Inspect and reuse relevant history, reproduce distinguishing failures, repair current source, verify the repaired cases, run current public regression tests, and report only actual current verification. These are previously taught development obligations combined in one episode.''')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(H.iterdir()) if p.is_file()}
(R/'complete-history-manifest.json').write_text(json.dumps(manifest,indent=2))
(R/'joint-freeze.json').write_text(json.dumps({'history':manifest,'source_sha256':hashlib.sha256(s.encode()).hexdigest(),'task':(work/'TASK.md').read_text(),'construction':'previously exposed filter non-None bug plus learner-developed .strip rename type bug; development acquisition, not fresh transfer'},indent=2))
