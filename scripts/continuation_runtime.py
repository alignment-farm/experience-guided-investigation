"""Strict development interface; original pilot runtime is intentionally preserved."""
import json
from runtime import ToolEnv

INSTRUCTIONS = '''You are a software maintenance agent in a fresh session.
Complete the ETL repair. Inspect source and eligible history, formulate a probe
that distinguishes the bug from the required behavior, edit and verify.
Reply with exactly ONE JSON object. No markdown, prose or multiple actions.
Actions:
{"action":"read","path":"etl_pipeline.py","start":1,"limit":100}
{"action":"search","path":".","pattern":"text"}
{"action":"history_search","pattern":"text"}
{"action":"test"}
{"action":"probe","payload":{"pipeline":{"steps":[]},"dataset":[]}}
{"action":"edit","path":"etl_pipeline.py","old":"exact text","new":"replacement"}
{"action":"done","message":"what was actually verified"}
read is paginated by line (up to 100). Probe can additionally include expected,
the full expected JSON output, to get an explicit assertion. Schema errors do
NOT demonstrate the requested behavior. Keep edits narrow. Only boolean true
is distinct from truthy numbers or strings. Use current TASK.md as the contract.
'''


def render(task, transcript):
    return INSTRUCTIONS + '\nCURRENT TASK:\n' + task + '\nTRANSCRIPT:\n' + (transcript or '(none)') + '\nReturn the next JSON action.'


def parse(raw):
    try:
        action = json.loads(raw.strip())
        if isinstance(action, dict) and isinstance(action.get('action'), str):
            return action
    except (ValueError, TypeError):
        pass
    return None


class Environment(ToolEnv):
    def call(self, action):
        if action.get('action') == 'read':
            self.calls += 1
            try:
                path = self._safe(action['path'])
                lines = path.read_text().splitlines()
                start = max(1, int(action.get('start', 1)))
                limit = max(1, min(100, int(action.get('limit', 100))))
                end = min(len(lines), start - 1 + limit)
                return {'ok': True, 'total_lines': len(lines), 'next_start': end + 1 if end < len(lines) else None,
                        'content': '\n'.join(f'{i+1}: {lines[i]}' for i in range(start-1, end))}
            except Exception as exc:
                return {'ok': False, 'error': str(exc)}
        result = super().call(action)
        if action.get('action') == 'probe' and 'stdout' in result:
            try:
                actual = json.loads(result['stdout'])
                result['application_ok'] = actual.get('status') == 'ok'
                if 'expected' in action:
                    result['assertion_passed'] = actual == action['expected']
            except ValueError:
                result['application_ok'] = False
        return result
