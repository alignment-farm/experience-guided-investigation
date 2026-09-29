"""Fresh bounded contract confirmation, frozen before joint acquisition outcomes."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from workload import write_workspace
R=Path('evidence/autonomy-03')
def cases():
 rows=[{'tag':'t','eligible':True},{'tag':'f','eligible':False},{'tag':'n','eligible':42},{'tag':'float','eligible':1.0},{'tag':'s','eligible':'true'},{'tag':'a','eligible':[1]},{'tag':'o','eligible':{'x':1}},{'tag':'null','eligible':None},{'tag':'absent'}]
 out=[{'name':'new_filter_values','steps':[{'op':'filter','where':'eligible'}],'rows':rows,'expect':[rows[0]]},{'name':'numeric_literal_not_boolean','steps':[{'op':'filter','where':'1'}],'rows':[{'z':8}],'expect':[]},{'name':'rename_filter_map_limit','steps':[{'op':'rename','from':' eligible ','to':' enabled '},{'op':'filter','where':'enabled'},{'op':'map','as':'copy','expr':'tag'},{'op':'limit','n':1}],'rows':rows[:6],'expect':[{'tag':'t','enabled':True,'copy':'t'}]}]
 for field,value,label in [('from',None,'null_from'),('to',3,'integer_to'),('to',True,'boolean_to'),('from',[],'array_from'),('to',' \t ','blank_to')]:
  step={'op':'rename','from':'a','to':'b'};step[field]=value;out.append({'name':label,'steps':[step],'rows':[],'error_code':'SCHEMA_VALIDATION_FAILED','error_path':'pipeline.steps[0].'+field})
 out += [{'name':'mapping_spaces_preserved','steps':[{'op':'rename','mapping':{' a ':' b '}}],'rows':[{' a ':7}],'expect':[{' b ':7}]},{'name':'rename_then_zero','steps':[{'op':'rename','from':' a ','to':' b '},{'op':'limit','n':0}],'rows':[{'a':7}],'expect':[]}]
 return out

def grade(work):
 records=[]
 for c in cases():
  p=subprocess.run([sys.executable,str(work/'etl_pipeline.py'),'--execute'],input=json.dumps({'pipeline':{'steps':c['steps']},'dataset':c['rows']}),text=True,capture_output=True,timeout=10)
  try:actual=json.loads(p.stdout)
  except ValueError:actual=None
  if 'error_code' in c:passed=p.returncode==1 and isinstance(actual,dict) and actual.get('error_code')==c['error_code'] and actual.get('path')==c['error_path']
  else:passed=p.returncode==0 and actual=={'status':'ok','data':c['expect'],'metrics':{'rows_in':len(c['rows']),'rows_out':len(c['expect'])}}
  records.append({'case':c,'actual':actual,'passed':bool(passed),'returncode':p.returncode,'stderr':p.stderr})
 return {'cases':records,'passed':sum(x['passed'] for x in records),'total':len(records),'complete':all(x['passed'] for x in records)}
if __name__=='__main__':
 if '--freeze' in sys.argv:
  target=R/'confirmation-freeze.json';assert not target.exists()
  with tempfile.TemporaryDirectory() as d:
   w=Path(d);write_workspace(w,'transfer-branch');result=grade(w);assert result['complete'],result
  target.write_text(json.dumps({'cases':cases(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reference':result,'selection':'Constructed from already stated contracts before joint acquisition outcomes; no participant or teacher access; not independent histories.'},indent=2));print('Frozen ten new contract cases; original reference passes.')
 else:
  reports={w.name:grade(w) for w in sorted((R/'workspaces').iterdir()) if (R/'runs'/w.name/'summary.json').exists()}
  (R/'confirmation-evaluation.json').write_text(json.dumps(reports,indent=2));print({k:v['passed'] for k,v in reports.items()})
