"""Inventory submitted-code imports and call names; not an OS sandbox proof."""
import ast,json
from pathlib import Path
from workload import BASE_SOURCE
R=Path('evidence/autonomy-03')
def inventory(source):
 tree=ast.parse(source);imports=[];calls=[]
 for node in ast.walk(tree):
  if isinstance(node,ast.Import):imports += [x.name for x in node.names]
  elif isinstance(node,ast.ImportFrom):imports += [node.module or '']
  elif isinstance(node,ast.Call):calls.append(ast.unparse(node.func))
 return set(imports),set(calls)
bi,bc=inventory(BASE_SOURCE);report={}
for p in sorted((R/'runs').glob('*/submitted.py')):
 try:
  i,c=inventory(p.read_text());report[p.parent.name]={'new_imports':sorted(i-bi),'new_call_names':sorted(c-bc)}
 except SyntaxError as e:report[p.parent.name]={'syntax_error':str(e)}
(R/'source-access-audit.json').write_text(json.dumps({'submissions':report,'boundary':'Direct read/search/restore paths are workspace-restricted. Python probe/test subprocesses are not independently OS-jailed; this inventory and full edit records support observed access audit, not an adversarial security proof. Future material is absent from supplied prompts/history. Inspect the listed changes and full edit records; an inventory alone is not proof against external I/O.'},indent=2));print(report)
