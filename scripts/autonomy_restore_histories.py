"""Restore exact deduplicated workspace history bytes from published manifests."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('evidence/autonomy-03'));a=p.parse_args();manifest=json.loads((a.root/'workspace-history-manifests.json').read_text());count=0
for folder,entries in manifest.items():
 for name,record in entries.items():
  data=(a.root/record['object']).read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256']
  target=a.root/folder/name
  if target.exists():assert target.read_bytes()==data,target
  else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  count+=1
print('Verified/restored',count,'history files without overwriting changed files.')
