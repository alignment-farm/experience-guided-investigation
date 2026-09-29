"""Shared native-dialogue maintenance tools; transport simplification only."""
import json
from pathlib import Path
from runtime import ToolEnv

SYSTEM='''You maintain an ETL Python program. Work autonomously using ONE JSON action
per reply, with no prose outside it. First use relevant past experience from the
history archive, then construct and run an input that distinguishes the required
behavior from the bug. Inspect the code, make a narrow edit, rerun your probe and
the regression suite, and finish only when the evidence supports completion.

Actions (one at a time):
{"action":"history_search","pattern":"filter"}
{"action":"read","path":"history/INDEX.md"}
{"action":"read","path":"etl_pipeline.py","start":1,"limit":250}
{"action":"search","path":".","pattern":"text"}
{"action":"probe","steps":[{"op":"limit","n":1}],"rows":[{"id":1},{"id":2}],"expect":[{"id":1}]}
{"action":"edit","old":"exact source text","new":"replacement source text"}
{"action":"test"}
{"action":"done","message":"what was actually verified"}

The probe fields are steps, rows, expect: expect is the complete expected OUTPUT
ROW ARRAY, not a CLI response object. For an expected application error instead,
use error_code and error_path. The tool constructs the CLI request and reports
actual rows plus assertion_passed. A schema error or false assertion is evidence
of a problem, never a successful verification. No tool chooses test cases or
expected answers for you. Expressions use Python syntax and bare column names.
Edit replaces exactly one source region. Reads show copyable code without line
number prefixes. If next_offset is set, read the same path/start with offset to
continue the same page. history/ contains complete eligible earlier attempts, executed
corrections and repaired code; retrieve and reuse these when useful. Source is
provided initially; further tools can inspect any visible source/history file.
'''


def parse(raw):
    text=raw.strip()
    if text.startswith('```') and text.endswith('```'):
        text='\n'.join(text.splitlines()[1:-1]).strip()
    try:
        value=json.loads(text)
        if isinstance(value,dict) and isinstance(value.get('action'),str):return value
    except ValueError:pass
    return None


def first_action(raw):
    text=raw.lstrip()
    if text.startswith('```'):
        if '\n' not in text:return None
        text=text.split('\n',1)[1].lstrip()
    if not text.startswith('{'):return None
    try:
        value,end=json.JSONDecoder().raw_decode(text)
        if isinstance(value,dict) and isinstance(value.get('action'),str):
            return value,text[:end]
    except ValueError:pass
    return None


class Environment(ToolEnv):
    def call(self,action):
        kind=action.get('action')
        if kind=='history_search':
            self.calls+=1
            pattern=str(action.get('pattern','')).lower()
            hits=[]
            for path in sorted((self.root/'history').glob('*')):
                if not path.is_file():continue
                for i,line in enumerate(path.read_text().splitlines(),1):
                    if pattern and pattern in line.lower():
                        hits.append({'path':str(path.relative_to(self.root)),'line':i,'excerpt':line[:180]})
                        break
            return {'ok':True,'matches':hits[:16],'matching_files':len(hits),'hint':'Read a returned path for its complete record; narrow your search if needed.'}
        if kind=='read':
            self.calls+=1
            try:
                path=self._safe(str(action['path']))
                if not path.exists() and '/' not in str(action['path']):
                    candidate=self._safe('history/'+str(action['path']))
                    if candidate.is_file():path=candidate
                lines=path.read_text().splitlines();start=max(1,int(action.get('start',1)));limit=max(1,min(250,int(action.get('limit',250))))
                end=min(len(lines),start-1+limit)
                content='\n'.join(lines[start-1:end]);offset=max(0,int(action.get('offset',0)));chunk=content[offset:offset+12000]
                return {'ok':True,'path':str(path.relative_to(self.root)),'start':start,'total_lines':len(lines),'next_start':end+1 if end<len(lines) else None,'next_offset':offset+len(chunk) if offset+len(chunk)<len(content) else None,'content':chunk}
            except Exception as exc:return {'ok':False,'error':str(exc)}
        if kind=='edit':action=dict(action,path='etl_pipeline.py')
        if kind=='probe':
            if not isinstance(action.get('steps'),list) or not isinstance(action.get('rows'),list) or (not isinstance(action.get('expect'),list) and 'error_code' not in action):
                self.calls+=1
                return {'ok':False,'assertion_passed':False,'error':'probe requires steps array, rows array, and expect output-row array (or error_code/error_path).'}
            result=super().call({'action':'probe','payload':{'pipeline':{'steps':action['steps']},'dataset':action['rows']}})
            try:actual=json.loads(result.get('stdout',''))
            except ValueError:actual=None
            application_ok=isinstance(actual,dict) and actual.get('status')=='ok' and result.get('returncode')==0
            if 'error_code' in action:
                passed=result.get('returncode')==1 and isinstance(actual,dict) and actual.get('error_code')==action['error_code'] and actual.get('path')==action.get('error_path')
            else:
                expected={'status':'ok','data':action['expect'],'metrics':{'rows_in':len(action['rows']),'rows_out':len(action['expect'])}}
                passed=application_ok and actual==expected
            return {'ok':result.get('ok',False),'application_ok':application_ok,'assertion_passed':bool(passed),'actual':actual,'expected_rows':action.get('expect'),'expected_error':action.get('error_code'),'returncode':result.get('returncode'),'stderr':result.get('stderr'),'seconds':result.get('seconds')}
        return super().call(action)


def initial_messages(workspace):
    return [{'role':'system','content':SYSTEM},{'role':'user','content':(workspace/'TASK.md').read_text()+'\n\nCURRENT SOURCE (etl_pipeline.py):\n'+(workspace/'etl_pipeline.py').read_text()+'\n\nHISTORY INDEX:\n'+(workspace/'history/INDEX.md').read_text()}]
