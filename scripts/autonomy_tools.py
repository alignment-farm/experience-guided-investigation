"""Native Qwen function schemas and one-call transport parsing."""
import json
from autonomy_runtime import Environment as BasicEnvironment,initial_messages as basic_messages

SYSTEM='''You are repairing the CURRENT ETL program autonomously. Use the provided
functions to inspect relevant past experience, construct a distinguishing test,
repair the current program, verify the test and preserved regression behavior,
and report completion truthfully. Use one function call at a time and wait for
its actual result. Source below is the current workspace. History files are PAST
records, not evidence that this workspace was changed or tested. Reading a past
correct program does not apply it: use edit or restore to reuse it, then verify
CURRENT execution. Do not confuse a tool's process success with an assertion
passing. Test the stated behavior, including contrasting boundary values when
relevant, rather than an unrelated operation. Expressions use Python syntax and
bare field names. Use replay to execute an applicable retained check directly, or probe to construct
a new one. You choose every action and test; no sequence is injected.'''


def schema(name,description,properties,required=()):
    return {'type':'function','function':{'name':name,'description':description,'parameters':{'type':'object','properties':properties,'required':list(required),'additionalProperties':False}}}
S={'type':'string'};I={'type':'integer'};ROWS={'type':'array','items':{'type':'object'}}
TOOLS=[
 schema('read','Read current code or a PAST history file. Copyable source; next_offset supports long records.',{'path':S,'start':I,'limit':I,'offset':I},['path']),
 schema('history_search','Find relevant PAST experience; returned paths are directly readable.',{'pattern':S},['pattern']),
 schema('search','Search current source or history for a literal substring.',{'path':S,'pattern':S},['pattern']),
 schema('probe','Execute CURRENT code on chosen pipeline steps and input rows; assert exact expected output row array. Reports actual result and assertion_passed. For expected errors use error_code/error_path instead of expect.',{'steps':{'type':'array','items':{'type':'object'}},'rows':ROWS,'expect':ROWS,'error_code':S,'error_path':S},['steps','rows']),
 schema('edit','Replace exactly one source region in CURRENT etl_pipeline.py. Old/new are exact code strings.',{'old':S,'new':S},['old','new']),
 schema('restore','Copy a chosen PAST Python source artifact into CURRENT etl_pipeline.py, then verify it fits the current task. This is ordinary code reuse; history is unchanged.',{'source':S},['source']),
 schema('replay','Execute a selected existing history check against CURRENT code. Reuses its recorded input and expected output unchanged; for a new requirement construct or adapt a probe instead.',{'case_id':{'type':'string','enum':['filter_boolean_only','rename_trim','limit_zero']}},['case_id']),
 schema('test','Run the current public regression suite. A passing suite need not cover the new requirement.',{}),
 schema('done','Declare current task completion, citing actual current verification. Past records are not current evidence.',{'message':S},['message'])]


def first_tool(raw):
    if '<tool_call>' not in raw:return None
    before,body=raw.split('<tool_call>',1)
    body=body.lstrip()
    try:value,end=json.JSONDecoder().raw_decode(body)
    except ValueError:return None
    if not isinstance(value,dict) or not isinstance(value.get('name'),str) or not isinstance(value.get('arguments'),dict):return None
    return {'action':value['name'],**value['arguments']},before.strip(),value


class Environment(BasicEnvironment):
    def call(self,action):
        if action.get('action')=='replay':
            try:
                cases=json.loads((self.root/'history/CASES.json').read_text());case=cases[action['case_id']]
                result=super().call(case['action']);result['replayed_case_id']=action['case_id'];result['expectation_origin']=case['expectation_origin'];return result
            except Exception as exc:
                self.calls+=1;return {'ok':False,'error':str(exc)}
        if action.get('action')=='restore':
            self.calls+=1
            try:
                path=self._safe(str(action['source']))
                if self.root/'history' not in path.parents or path.suffix!='.py':return {'ok':False,'error':'restore.source must be a Python source file under history/'}
                source=path.read_text();compile(source,str(path),'exec')
                (self.root/'etl_pipeline.py').write_text(source)
                return {'ok':True,'restored_from':str(path.relative_to(self.root)),'written':'etl_pipeline.py','bytes':len(source.encode()),'reminder':'CURRENT source changed; now run your distinguishing probe and regression tests.'}
            except Exception as exc:return {'ok':False,'error':str(exc)}
        return super().call(action)


def initial_messages(workspace):
    messages=basic_messages(workspace);messages[0]['content']=SYSTEM
    return messages
