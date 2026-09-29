"""Inventory redundant participant history copies and preserve all unique bytes."""
import hashlib,json,shutil
from pathlib import Path
R=Path('evidence/autonomy-03');objects={}
for folder in ['history','reuse-history','complete-history','fresh-history','history-objects']:
 root=R/folder
 if root.exists():
  for p in sorted(root.rglob('*')):
   if p.is_file():objects.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(),str(p.relative_to(R)))
manifest={}
roots=list((R/'workspaces').glob('*/history'))+list((R/'acquisition').glob('*/workspace/history'))
for root in sorted(roots):
 entries={}
 for p in sorted(root.rglob('*')):
  if not p.is_file():continue
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  if digest not in objects:
   target=R/'history-objects'/digest;target.parent.mkdir(exist_ok=True);shutil.copy2(p,target);objects[digest]=str(target.relative_to(R))
  entries[str(p.relative_to(root))]={'sha256':digest,'object':objects[digest]}
 manifest[str(root.relative_to(R))]=entries
(R/'workspace-history-manifests.json').write_text(json.dumps(manifest,indent=2))
print('Inventoried',len(manifest),'workspace histories; every byte retained in shared archives.')
